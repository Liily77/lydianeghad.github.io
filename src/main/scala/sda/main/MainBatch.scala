package sda.main
import org.apache.spark.sql.SparkSession
import sda.args._
import sda.parser.ConfigurationParser
import sda.traitement.ServiceVente._

object MainBatch {
  def main(args: Array[String]): Unit = {
    implicit val spark: SparkSession = SparkSession
      .builder
      .appName("SDA")
      .config("spark.master", "local")
      .getOrCreate()

    // Set Spark's legacy time parser policy
    spark.conf.set("spark.sql.legacy.timeParserPolicy", "LEGACY")

    // Parse input arguments
    Args.parseArguments(args)

    // Match the reader type and get the appropriate configuration
    val reader = Args.readertype match {
      case "csv" => ConfigurationParser.getCsvReaderConfigurationFromJson(Args.readerConfigurationFile)
      case "json" => ConfigurationParser.getJsonReaderConfigurationFromJson(Args.readerConfigurationFile)
      case "xml" => ConfigurationParser.getXmlReaderConfigurationFromJson(Args.readerConfigurationFile)
      case _ => throw new Exception("Invalid reader type. Supported reader formats: csv, json, and xml.")
    }

    // Read the data
    val df = reader.read()

    // Print schema to verify columns
    df.printSchema()
    df.show(5)

    // Ensure DataFrameUtils methods are used
    val dfFormatted = df.formatter()

    // Calculate TTC and process data
    dfFormatted.createfake().show()
    println("***********************Resultat Question1*****************************")
    dfFormatted.show(20)
    println("***********************Resultat Question2*****************************")
    dfFormatted.calculTTC().show(20)
    println("***********************Resultat Question3*****************************")
    val dfWithDateVille = dfFormatted.calculTTC().extractDateEndContratVille()
    dfWithDateVille.show()
    println("***********************Resultat Question4*****************************")
    dfWithDateVille.contratStatus().show(20)

    spark.stop()
  }
}
