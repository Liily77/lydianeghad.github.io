name := "projet_sda_2024"

version := "1.0"

scalaVersion := "2.12.15"

// Dependencies
libraryDependencies ++= Seq(
  "org.apache.spark" %% "spark-sql" % "3.3.1",
  "com.beust" % "jcommander" % "1.48",
  "org.scalatest" %% "scalatest" % "3.2.10" % Test,
  "org.apache.spark" %% "spark-core" % "3.3.1",
  "org.apache.logging.log4j" % "log4j-core" % "2.17.2",
  "org.apache.logging.log4j" % "log4j-api" % "2.17.2",
  "org.apache.logging.log4j" % "log4j-slf4j-impl" % "2.17.2"
)

// Main class for assembly
Compile / mainClass := Some("sda.main.MainBatch")

// Assembly merge strategy
assembly / assemblyMergeStrategy := {
  case PathList("META-INF", xs @ _*) => MergeStrategy.discard
  case "log4j2.xml" => MergeStrategy.first
  case _ => MergeStrategy.first
}

// Resolvers
resolvers ++= Seq(
  Resolver.mavenCentral,
  Resolver.sonatypeRepo("public"),
  "Scala Tools Releases" at "https://oss.sonatype.org/content/repositories/releases/"
)
