package sda.traitement

import org.apache.spark.sql.SparkSession
import org.scalatest.funsuite.AnyFunSuite

class CalculTTCTest extends AnyFunSuite {

  val spark: SparkSession = SparkSession
    .builder
    .appName("Test")
    .config("spark.master", "local")
    .getOrCreate()

  import spark.implicits._
  import ServiceVente._

  test("calculTTC calculates TTC correctly") {
    val df = Seq(
      ("1", "100,5|0,19"),
      ("2", "120,546|0,20")
    ).toDF("Id_Client", "HTT_TVA")

    val resultDF = df.calculTTC()

    val expectedDF = Seq(
      ("1", "100,5|0,19", 119.60),
      ("2", "120,546|0,20", 144.66)
    ).toDF("Id_Client", "HTT_TVA", "TTC")

    assert(resultDF.collect() sameElements expectedDF.collect())
  }
}
