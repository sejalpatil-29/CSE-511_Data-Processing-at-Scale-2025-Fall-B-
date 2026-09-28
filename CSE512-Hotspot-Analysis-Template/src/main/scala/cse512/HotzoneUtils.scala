package cse512

object HotzoneUtils {

  def ST_Contains(queryRectangle: String, pointString: String): Boolean = {
    // Parse rectangle coordinates
    val rectArray = queryRectangle.split(",")
    val x1 = rectArray(0).trim.toDouble
    val y1 = rectArray(1).trim.toDouble
    val x2 = rectArray(2).trim.toDouble
    val y2 = rectArray(3).trim.toDouble

    // Determine rectangle boundaries (handles any order)
    val xMin = Math.min(x1, x2)
    val xMax = Math.max(x1, x2)
    val yMin = Math.min(y1, y2)
    val yMax = Math.max(y1, y2)

    // Parse point coordinates
    val pointArray = pointString.split(",")
    val x = pointArray(0).trim.toDouble
    val y = pointArray(1).trim.toDouble

    // Return true if point lies inside or on the boundary of rectangle
    (x >= xMin && x <= xMax && y >= yMin && y <= yMax)
  }

}







