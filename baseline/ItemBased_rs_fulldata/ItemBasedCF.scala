import java.io.{File, PrintWriter}

import org.apache.spark.{SparkConf, SparkContext}

import scala.collection.immutable.Map
import scala.collection.mutable

object ItemBased {

  def main(args: Array[String]): Unit = {
    val conf = new SparkConf()
    conf.setAppName("ItemBased")
    conf.setMaster("local")
    val sc = new SparkContext(conf)
    
    val raw_training_data = sc.textFile("/Users/dwj/CSCI553/HW/Project/yelp-recommendation-system/baseline/data/train_data_full.csv")
    val training_header = raw_training_data.first()
    val parsed_training_data = raw_training_data.filter(row => row != training_header).map(_.split(','))

    val raw_testing_data = sc.textFile("/Users/dwj/CSCI553/HW/Project/yelp-recommendation-system/baseline/data/test_data_full.csv")
    val testing_header = raw_testing_data.first()
    val parsed_testing_data = raw_testing_data.filter(row => row != testing_header).map(_.split(','))

    val start_time = System.nanoTime()

    //distinct users: 1518169
    val users = parsed_training_data.union(parsed_testing_data)
      .map { case Array(user, business, star) => (user, 1) }
      .reduceByKey(_ + _)
      .sortByKey()
      .map(_._1)
      .collect()
      .toList
    val user_map = new mutable.HashMap[String, Int]()
    val user_list = new mutable.HashMap[Int, String]()
    for ((x, i) <- users.view.zipWithIndex) {
      user_map(x) = i
      user_list(i) = x
    }

    val businesses = parsed_training_data.union(parsed_testing_data)
      .map { case Array(user, business, star) => (business, 1) }
      .reduceByKey(_ + _)
      .sortByKey()
      .map(_._1)
      .collect()
      .toList
    val business_map = new mutable.HashMap[String, Int]()
    val business_list = new mutable.HashMap[Int, String]()
    for ((x, i) <- businesses.view.zipWithIndex) {
      business_map(x) = i
      business_list(i) = x
    }

    val training_ratings = parsed_training_data.map {
      case Array(user, business, stars) => (user_map(user), business_map(business), stars.toDouble.toInt)
    }

    val testing_ratings = parsed_testing_data.map {
      case Array(user, business, stars) => (user_map(user), business_map(business), stars.toDouble.toInt)
    }

    val user_ratings = training_ratings.map { case (user, business, rating) => (user, (business, rating)) }
      .combineByKey(
        tuple => Map(tuple),
        (c: Map[Int, Int], tuple) => c + tuple,
        (c1: Map[Int, Int], c2: Map[Int, Int]) => c1 ++ c2
      )
    val user_ratings_map = user_ratings.collectAsMap()

    val overall_avg = training_ratings.map(_._3).mean()

    val user_avg = user_ratings.mapValues(reviews => {
      var sum = 0
      reviews.values.foreach(x => sum += x)
      sum.toDouble / reviews.size
    })
    val user_avg_map = user_avg.collectAsMap()

    val user_normalized_ratings = user_ratings.join(user_avg)
      .mapValues { case (reviews, avg) =>
        reviews.map(review => (review._1, review._2 - avg))
      }
    val user_normalized_ratings_map = user_normalized_ratings.collectAsMap()

    val business_ratings = training_ratings.map { case (user, business, rating) => (business, (user, rating)) }
      .combineByKey(
        tuple => Map(tuple),
        (c: Map[Int, Int], tuple) => c + tuple,
        (c1: Map[Int, Int], c2: Map[Int, Int]) => c1 ++ c2
      )
    val business_ratings_map = business_ratings.collectAsMap()

    val business_normalized_ratings = business_ratings.mapValues(reviews =>
      reviews.map { case (user, rating) => (user, rating - user_avg_map(user)) })
    val business_normalized_ratings_map = business_normalized_ratings.collectAsMap()

    val user_based_neighbourhood_size = 1
    val item_based_neighbourhood_size = 3

    // evaluation begins
    val requests = testing_ratings.map { case (user, business, rate) => (user, business) }

    val user_based_predictions = requests.combineByKey(
      business => Set(business),
      (c: Set[Int], business) => c + business,
      (c1: Set[Int], c2: Set[Int]) => c1 ++ c2
    ).leftOuterJoin(user_avg).leftOuterJoin(user_normalized_ratings).mapValues {
      case ((query_businesses, avg), normalized_ratings) =>
        if (avg.isEmpty) {
          query_businesses.map(business => {
            if (business_ratings_map.contains(business)) {
              var sum = 0
              business_ratings_map(business).values.foreach(x => sum += x)
              (business, sum.toDouble / business_ratings_map(business).size, 0.0001)
            } else {
              (business, overall_avg, 0.000001)
            }
          })
        } else {
          var related_users = new mutable.HashSet[Int]
          query_businesses.foreach(business => {
            if (business_ratings_map.contains(business)) {
              related_users ++= business_ratings_map(business).keySet
            }
          })
          val similarity = new mutable.HashMap[Int, Double]
          related_users.foreach(related_user => {
            var sim: Double = 0
            var norm1: Double = 0
            var norm2: Double = 0
            val related_ratings: Map[Int, Double] = user_normalized_ratings_map(related_user)
            val curr_ratings: Map[Int, Double] = normalized_ratings.get
            related_ratings.keySet.intersect(curr_ratings.keySet).foreach(
              business => {
                sim += related_ratings(business) * curr_ratings(business)
                norm1 += related_ratings(business) * related_ratings(business)
                norm2 += curr_ratings(business) * curr_ratings(business)
              })
            if (norm1 != 0 && norm2 != 0) {
              similarity(related_user) = sim / Math.sqrt(norm1) / Math.sqrt(norm2)
            }
          })
          query_businesses.map(business => {
            if (!business_normalized_ratings_map.contains(business)) {
              (business, avg.get, 0.0001)
            } else {
              val neighbours = new mutable.PriorityQueue[(Double, Double)]()
              business_normalized_ratings_map(business).foreach { case (user, rating) =>
                if (similarity.contains(user)) {
                  neighbours += ((-similarity(user), rating))
                }
                if (neighbours.size > user_based_neighbourhood_size) {
                  neighbours.dequeue()
                }
              }

              var sim: Double = 0
              var norm: Double = 0
              neighbours.foreach { case (neg_similarity, rating) =>
                sim += rating * -neg_similarity
                norm += Math.abs(neg_similarity)
              }
              if (norm == 0) {
                (business, avg.get, 0.0001)
              } else {
                (business, avg.get + sim / norm, norm * 100 / user_based_neighbourhood_size)
              }
            }
          })
        }
    }.flatMap { case (user, prediction_list) =>
      prediction_list.map { case (business, prediction, confidence) => ((user, business), (prediction, confidence)) }
    }

    val item_based_predictions = requests.map { case (user, business) => (business, user) }
      .combineByKey(
        user => Set(user),
        (c: Set[Int], user) => c + user,
        (c1: Set[Int], c2: Set[Int]) => c1 ++ c2
      ).leftOuterJoin(business_normalized_ratings).mapValues {
      case (query_users, normalized_ratings) =>
        if (normalized_ratings.isEmpty) {
          query_users.map(user => {
            if (user_avg_map.contains(user)) {
              (user, user_avg_map(user), 0.0001)
            } else {
              (user, overall_avg, 0.000001)
            }
          })
        } else {
          var related_businesses = new mutable.HashSet[Int]
          query_users.foreach(user => {
            if (user_normalized_ratings_map.contains(user)) {
              related_businesses ++= user_normalized_ratings_map(user).keySet
            }
          })
          val similarity = new mutable.HashMap[Int, Double]
          related_businesses.foreach(related_business => {
            var sim: Double = 0
            var norm1: Double = 0
            var norm2: Double = 0
            val related_ratings: Map[Int, Double] = business_normalized_ratings_map(related_business)
            val curr_ratings: Map[Int, Double] = normalized_ratings.get
            related_ratings.keySet.intersect(curr_ratings.keySet).foreach(
              user => {
                sim += related_ratings(user) * curr_ratings(user)
                norm1 += related_ratings(user) * related_ratings(user)
                norm2 += curr_ratings(user) * curr_ratings(user)
              })
            if (norm1 != 0 && norm2 != 0) {
              similarity(related_business) = sim / Math.sqrt(norm1) / Math.sqrt(norm2)
            }
          })
          query_users.map(user => {
            if (!user_normalized_ratings_map.contains(user)) {
              (user, overall_avg, 0.000001)
            } else {
              val neighbours = new mutable.PriorityQueue[(Double, Double)]()
              user_ratings_map(user).foreach { case (business, rating) =>
                if (similarity.contains(business)) {
                  neighbours += ((-similarity(business), rating))
                }
                if (neighbours.size > item_based_neighbourhood_size) {
                  neighbours.dequeue()
                }
              }

              var sim: Double = 0
              var norm: Double = 0
              neighbours.foreach { case (neg_similarity, rating) =>
                sim += rating * -neg_similarity
                norm += Math.abs(neg_similarity)
              }
              if (norm == 0) {
                (user, overall_avg, 0.000001)
              } else {
                (user, sim / norm, norm * 100 / item_based_neighbourhood_size)
              }
            }
          })
        }
    }.flatMap { case (business, prediction_list) =>
      prediction_list.map { case (user, prediction, confidence) => ((user, business), (prediction, confidence)) }
    }

    val predictions = user_based_predictions.join(item_based_predictions).mapValues {
      case ((user_pred, user_conf), (item_pred, item_conf)) =>
        (user_pred * user_conf + item_pred * item_conf) / (user_conf + item_conf)
    }

    val min_pred = predictions.map(_._2).min()
    val max_pred = predictions.map(_._2).max()
    val normalized_predictions = predictions.mapValues(prediction =>
      if (prediction == overall_avg) overall_avg else (prediction - min_pred) / (max_pred - min_pred) * 4 + 1)

    val end_time = System.nanoTime()
    val elapsed_time: Long = (end_time - start_time) / 1000000000

    val sorted_predictions = normalized_predictions.map { case ((user, business), rate) =>
      user_list(user) + ',' + business_list(business) + ',' + rate.toString + '\n'
    }.collect()

    val output_file = new File("/Users/dwj/CSCI553/HW/HW1/ItemBasedCF.txt")

    val pw = new PrintWriter(output_file)
    for (row <- sorted_predictions) {
      pw.write(row)
    }
    pw.close()

    val ratesAndPreds = testing_ratings.map { case (user, business, rating) => ((user, business), rating) }
      .join(normalized_predictions)

    // val distribution = ratesAndPreds.map { case ((user, business), (gt, prediction)) =>
    //   val x: Int = Math.floor(Math.abs(gt - prediction)).toInt
    //   if (x >= 4) {
    //     (">=4", 1)
    //   } else {
    //     (s">=$x and <${x + 1}", 1)
    //   }
    // }.reduceByKey(_ + _)
    //   .sortByKey()
    //   .map(item => item._1 + ": " + item._2.toString)
    //   .collect()


    val MSE = ratesAndPreds.map { case ((user, business), (r1, r2)) =>
      val err = r1 - r2
      err * err
    }.mean()

    val RMSE = Math.sqrt(MSE)

    // distribution.foreach(println)
    println(s"RMSE: $RMSE")
    println(s"Time: $elapsed_time sec")
    sc.stop()
  }
}
