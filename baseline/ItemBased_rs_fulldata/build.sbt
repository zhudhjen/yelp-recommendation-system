name := "ItemBased"
version := "0.1"
scalaVersion := "2.11.12"

artifactName in Compile := { (config: sbt.ScalaVersion, module: sbt.ModuleID, artifact: sbt.Artifact) =>
  artifact.name + "." + artifact.extension
}

libraryDependencies += "org.apache.spark" %% "spark-core" % "2.3.1"