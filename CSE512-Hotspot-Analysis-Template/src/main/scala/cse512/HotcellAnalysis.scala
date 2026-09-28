package cse512

import org.apache.log4j.{Level, Logger}
import org.apache.spark.sql.{DataFrame, SparkSession}
import org.apache.spark.sql.functions.udf
import org.apache.spark.sql.functions._

object HotcellAnalysis {
  Logger.getLogger("org.spark_project").setLevel(Level.WARN)
  Logger.getLogger("org.apache").setLevel(Level.WARN)
  Logger.getLogger("akka").setLevel(Level.WARN)
  Logger.getLogger("com").setLevel(Level.WARN)

def runHotcellAnalysis(spark: SparkSession, pointPath: String): DataFrame =
{
  // Load the original data from a data source
  var pickupInfo = spark.read.format("com.databricks.spark.csv").option("delimiter",";").option("header","false").load(pointPath);
  pickupInfo.createOrReplaceTempView("nyctaxitrips")
  pickupInfo.show()

  // Assign cell coordinates based on pickup points
  spark.udf.register("CalculateX",(pickupPoint: String)=>((
    HotcellUtils.CalculateCoordinate(pickupPoint, 0)
    )))
  spark.udf.register("CalculateY",(pickupPoint: String)=>((
    HotcellUtils.CalculateCoordinate(pickupPoint, 1)
    )))
  spark.udf.register("CalculateZ",(pickupTime: String)=>((
    HotcellUtils.CalculateCoordinate(pickupTime, 2)
    )))
  pickupInfo = spark.sql("select CalculateX(nyctaxitrips._c5),CalculateY(nyctaxitrips._c5), CalculateZ(nyctaxitrips._c1) from nyctaxitrips")
  //var newCoordinateName = Seq("x", "y", "z")
  pickupInfo = pickupInfo.toDF("x", "y", "z")
  pickupInfo.show()

  // Define the min and max of x, y, z
  val minX = -74.50/HotcellUtils.coordinateStep
  val maxX = -73.70/HotcellUtils.coordinateStep
  val minY = 40.50/HotcellUtils.coordinateStep
  val maxY = 40.90/HotcellUtils.coordinateStep
  val minZ = 1
  val maxZ = 31
  val numCells = (maxX - minX + 1)*(maxY - minY + 1)*(maxZ - minZ + 1)

  // YOU NEED TO CHANGE THIS PART
  
  pickupInfo.createOrReplaceTempView("pickupInfo")
  pickupInfo = spark.sql(
    "SELECT x, y, z FROM pickupInfo " +
    "WHERE x >= " + minX + " AND x <= " + maxX +
    " AND y >= " + minY + " AND y <= " + maxY +
    " AND z >= " + minZ + " AND z <= " + maxZ
  )

  pickupInfo = spark.sql("SELECT x, y, z, COUNT(*) AS count FROM pickupInfo GROUP BY x, y, z")
  pickupInfo.createOrReplaceTempView("pickupInfo")

  spark.udf.register("countNeighbors", (x: Int, y: Int, z: Int) =>
    HotcellUtils.countNeighbors(x, y, z, minX.toInt, maxX.toInt, minY.toInt, maxY.toInt, minZ, maxZ)
  )

  val neighborDf = spark.sql(
    "SELECT p1.x, p1.y, p1.z, " +
    "SUM(p2.count) AS sumNeighbors, " +
    "countNeighbors(p1.x, p1.y, p1.z) AS numNeighbors " +
    "FROM pickupInfo p1, pickupInfo p2 " +
    "WHERE (p2.x BETWEEN p1.x-1 AND p1.x+1) " +
    "AND (p2.y BETWEEN p1.y-1 AND p1.y+1) " +
    "AND (p2.z BETWEEN p1.z-1 AND p1.z+1) " +
    "GROUP BY p1.x, p1.y, p1.z"
  )

  val totalCount = spark.sql("SELECT SUM(count) FROM pickupInfo").first().getLong(0)
  val mean = totalCount.toDouble / numCells
  val variance = spark.sql("SELECT SUM(count*count) FROM pickupInfo").first().getLong(0).toDouble / numCells - mean*mean
  val stdDev = math.sqrt(variance)

  spark.udf.register("calculateGScore", (sumNeighbors: Int, numNeighbors: Int) =>
    HotcellUtils.calculateGScore(sumNeighbors, numNeighbors, mean, stdDev, numCells.toInt)
  )

  neighborDf.createOrReplaceTempView("neighbors")
  val resultDf = spark.sql(
    "SELECT x, y, z, calculateGScore(sumNeighbors, numNeighbors) AS gscore " +
    "FROM neighbors " +
    "ORDER BY gscore DESC"
  )

  resultDf.select("x","y","z").show(50)
  return resultDf.select("x","y","z") // YOU NEED TO CHANGE THIS PART
}
}


