package cse512

import java.sql.Timestamp
import java.text.SimpleDateFormat
import java.util.Calendar

object HotcellUtils {
  val coordinateStep = 0.01

  def CalculateCoordinate(inputString: String, coordinateOffset: Int): Int =
  {
    // Configuration variable:
    // Coordinate step is the size of each cell on x and y
    var result = 0
    coordinateOffset match
    {
      case 0 => result = Math.floor((inputString.split(",")(0).replace("(","").toDouble/coordinateStep)).toInt
      case 1 => result = Math.floor(inputString.split(",")(1).replace(")","").toDouble/coordinateStep).toInt
      // We only consider the data from 2009 to 2012 inclusively, 4 years in total. Week 0 Day 0 is 2009-01-01
      case 2 => {
        val timestamp = HotcellUtils.timestampParser(inputString)
        result = HotcellUtils.dayOfMonth(timestamp) // Assume every month has 31 days
      }
    }
    return result
  }

  def timestampParser (timestampString: String): Timestamp =
  {
    val dateFormat = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss")
    val parsedDate = dateFormat.parse(timestampString)
    val timeStamp = new Timestamp(parsedDate.getTime)
    return timeStamp
  }

  def dayOfYear (timestamp: Timestamp): Int =
  {
    val calendar = Calendar.getInstance
    calendar.setTimeInMillis(timestamp.getTime)
    return calendar.get(Calendar.DAY_OF_YEAR)
  }

  def dayOfMonth (timestamp: Timestamp): Int =
  {
    val calendar = Calendar.getInstance
    calendar.setTimeInMillis(timestamp.getTime)
    return calendar.get(Calendar.DAY_OF_MONTH)
  }

  // YOU NEED TO CHANGE THIS PART
  def countNeighbors(x: Int, y: Int, z: Int, minX: Int, maxX: Int, minY: Int, maxY: Int, minZ: Int, maxZ: Int): Int = {
  var count = 0
  
  for (dx <- -1 to 1; dy <- -1 to 1; dz <- -1 to 1) {
    val nx = x + dx
    val ny = y + dy
    val nz = z + dz
    if (nx >= minX && nx <= maxX && ny >= minY && ny <= maxY && nz >= minZ && nz <= maxZ) {
      count += 1
    }
  }
  count
}

def calculateGScore(sumNeighbors: Int, numNeighbors: Int, mean: Double, stdDev: Double, numCells: Int): Double = {
  val numerator = sumNeighbors.toDouble - mean * numNeighbors
  val denominator = stdDev * math.sqrt((numCells * numNeighbors - numNeighbors * numNeighbors).toDouble / (numCells - 1))
  numerator / denominator
}
}


