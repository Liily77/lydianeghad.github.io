package sda.traitement

import org.apache.spark.sql.SparkSession
import org.scalatest.funsuite.AnyFunSuite
import org.apache.spark.sql.functions._

class ServiceVenteTest extends AnyFunSuite {

  val spark: SparkSession = SparkSession
    .builder
    .appName("Test")
    .config("spark.master", "local")
    .getOrCreate()

  import spark.implicits._
  import ServiceVente._

  test("formatter splits HTT_TVA into HTT and TVA") {
    val df = Seq(
      ("1", "100,5|0,19"),
      ("2", "120,546|0,20")
    ).toDF("Id_Client", "HTT_TVA")

    val resultDF = df.formatter()

    val expectedDF = Seq(
      ("1", "100,5|0,19", "100,5", "0,19"),
      ("2", "120,546|0,20", "120,546", "0,20")
    ).toDF("Id_Client", "HTT_TVA", "HTT", "TVA")

    assert(resultDF.collect() sameElements expectedDF.collect())
  }
}
