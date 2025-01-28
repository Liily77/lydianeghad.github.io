
package sda.parser

import org.json4s.DefaultFormats
import org.json4s.jackson.JsonMethods
import sda.reader._

object ConfigurationParser {

  implicit val format = DefaultFormats

  def getCsvReaderConfigurationFromJson(jsonString: String): CsvReader = {
    JsonMethods.parse(FileReaderUsingIOSource.getContent(jsonString)).extract[CsvReader]
  }

  def getJsonReaderConfigurationFromJson(jsonString: String): JsonReader = {
    JsonMethods.parse(FileReaderUsingIOSource.getContent(jsonString)).extract[JsonReader]
  }

  def getXmlReaderConfigurationFromJson(jsonString: String): XmlReader = {
    JsonMethods.parse(FileReaderUsingIOSource.getContent(jsonString)).extract[XmlReader]
  }
}
