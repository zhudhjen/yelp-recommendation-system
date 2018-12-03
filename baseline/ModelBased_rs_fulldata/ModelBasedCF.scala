import org.apache.spark.{SparkContext, SparkConf}
import org.apache.spark.mllib.recommendation.ALS
import org.apache.spark.mllib.recommendation.MatrixFactorizationModel
import org.apache.spark.mllib.recommendation.Rating
import scala.collection.mutable.ListBuffer
import scala.collection.mutable.ArrayBuffer
import scala.collection.mutable.Map
import scala.collection.JavaConversions._
import scala.math
import java.io._
import java.io.BufferedWriter

object ModelBasedCF {  
  def main(args: Array[String]) {  
    val conf = new SparkConf().setAppName("ModelBasedCF")
    val sc = new SparkContext(conf)
    var userid_dict:Map[String,Int] = Map()
    var businessid_dict:Map[String,Int] = Map()
    var iduser_dict: Map[Int,String] = Map()
    var idbusi_dict:Map[Int,String] = Map()
    //var trainFile = sc.textFile(args{0})
    def getUser(user_string: String): Int = {
        return userid_dict(user_string)
    }

    def getBusiness(busi_string: String): Int = {
        return businessid_dict(busi_string)
    }

    def getOrigUser(user_id: Int): String = {
        return iduser_dict(user_id)
    }
   
    def getOrigBuis(busi_id: Int): String = {
        return idbusi_dict(busi_id)
    }
    
    def getDiff(one: Double, two: Double): String = {
        var abs_diff = math.abs(one - two)
        if (abs_diff < 1) {
            return ">=0 and <1:"
        } else if(abs_diff < 2) {
            return ">=1 and <2:"
        } else if(abs_diff < 3) {
            return ">=2 and <3:"
        } else if(abs_diff < 4) {
            return ">=3 and <4:"
        } else {
            return ">=4:"
        }
    }
    val t0 = System.nanoTime()

    
    var trainFile = sc.textFile("/Users/dwj/CSCI553/HW/Project/yelp-recommendation-system/baseline/data/train_data_full.csv")
    var header = trainFile.first() 
    var inputFileNoHeader = trainFile.filter(row => row != header).persist()
    var train_data = inputFileNoHeader.map(_.split(',') match { case Array(user, business, rate) => (user, business, rate.toDouble) }).persist()
    
    var first = train_data.map(line => (line._1, line)).reduceByKey((x,y) => x).collect()
    var userid_uniq = first.length
    
    var i = 0
    while(i < userid_uniq){
        userid_dict += (first(i)._1 -> i)
        iduser_dict += (i -> first(i)._1)
        i += 1
    }

    var second= train_data.map(line => (line._2, line)).reduceByKey((x,y) => x).collect()
    var busid_uniq = second.length
    i = 0
    while(i < busid_uniq){
        businessid_dict += (second(i)._1 -> i)
        idbusi_dict += (i -> second(i)._1)
        i += 1
    }
 
    var train_ratings = train_data.map(line => Rating(getUser(line._1), getBusiness(line._2), line._3.toDouble))
    // Build the recommendation model using ALS
    var rank = 2
    var numIterations = 24
    var lambda_als = 0.3
    
    val model = ALS.train(train_ratings, rank, numIterations, lambda_als)
    //var textFile = sc.textFile(args{1})
    var textFile = sc.textFile("/Users/dwj/CSCI553/HW/Project/yelp-recommendation-system/baseline/data/test_data_full.csv")
    header = textFile.first() 
    inputFileNoHeader = textFile.filter(row => row != header).persist()
    var test_data = inputFileNoHeader.map(_.split(',') match { case Array(user, business, rate) => (user, business, rate.toDouble) }).persist()

    first = test_data.map(line => (line._1, line)).reduceByKey((x,y) => x).collect()
    i = 0
    while(i < first.length){
        if(!userid_dict.contains(first(i)._1)){
            userid_dict += (first(i)._1 -> userid_uniq)
            userid_uniq += 1
        }
        i += 1
    }
    second= test_data.map(line => (line._2, line)).reduceByKey((x,y) => x).collect()
    i=0
    while(i < second.length){
        if(!businessid_dict.contains(second(i)._1)){
            businessid_dict += (second(i)._1 -> busid_uniq)
            busid_uniq += 1
        }
        i += 1
    }

    var test_ratings = test_data.map(line => Rating(getUser(line._1), getBusiness(line._2), line._3.toDouble))
    val usersBusiness = test_ratings.map { case Rating(user, business, rate) => (user, business) }
    val predictions = model.predict(usersBusiness).map { case Rating(user, business, rate) => ((user, business), rate) }
    val ratesAndPreds = test_ratings.map { case Rating(user, business, rate) => ((user, business), rate) }.join(predictions)
    // var result_statistic = ratesAndPreds.map{ case ((user, business), (r1, r2)) => (getDiff(r1, r2), 1)}.persist()
    // var result_statistic_final = result_statistic.reduceByKey((x,y) => x + y).sortByKey(true).collect()

    val MSE = ratesAndPreds.map { case ((user, business), (r1, r2)) =>
        val err = (r1 - r2)
        err * err
    }.mean()
    var RMSE = math.sqrt(MSE)
    // i=0
    // while(i < result_statistic_final.length){
    //     println(result_statistic_final(i)._1 + " " + result_statistic_final(i)._2.toString)
    //     i += 1
    // }
    println("RMSE:" + " " + RMSE.toString)
    val t4 = System.nanoTime()
    println("Time:" + " " + ((t4 - t0) * 1.0 /1000000000).toString)

    var true_predictions = predictions.map(line => ((getOrigUser(line._1._1), getOrigBuis(line._1._2)), line._2)).sortByKey(true).collect()
    var writer = new PrintWriter(new File("/Users/dwj/CSCI553/HW/HW1/modelBasedCF.txt"))
    i = 0
    while(i < true_predictions.length) {
        writer.write(true_predictions(i)._1._1 + ", " + true_predictions(i)._1._2 + ", " + true_predictions(i)._2.toString + "\n")
        i += 1
    }     
    writer.close()

  }  
}