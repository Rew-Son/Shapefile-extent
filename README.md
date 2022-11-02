# Shapefile-extent
Creating shapefile boundaries based on shapefile attributes. 
The purpose of the application is to generate boundaries of points, lines and polygons from a shapefile based on its attributes. The application uses libraries such as geopandas, numpy, shapely and sklearn. The GUI form was designed by PySimpleGUI. The final stage of application development was to create an executable file using pyinstaller. 

## Interface
![image](https://user-images.githubusercontent.com/71393344/198548661-d93badbe-6a25-4aab-b4c7-860ad27ff712.png)

## First step
Read all shapefiles in selected folder
![image](https://user-images.githubusercontent.com/71393344/198587197-4557012d-14e8-45d0-8a1c-1d714567d3b1.png)

## Second step
Read excel with attributes to merge
![image](https://user-images.githubusercontent.com/71393344/198549752-1810a7da-3809-46e1-95cc-69eebebf53ac.png)

## Third step
Set a size of bounds buffor.
Default value is 5m. 
![image](https://user-images.githubusercontent.com/71393344/198549982-57b7de93-dd1c-4ce9-931c-79cfaaa77b39.png)

## Fourth step
Choose output coordinate system, it should be the same as the coordinate system of input shapes.
![image](https://user-images.githubusercontent.com/71393344/198550436-9effc28b-60db-4067-9287-e0a4323aed1b.png)

## Fifth step
Submit the algorithm.
![image](https://user-images.githubusercontent.com/71393344/199437736-591af894-e479-4b30-bd72-023e951ff7af.png)

