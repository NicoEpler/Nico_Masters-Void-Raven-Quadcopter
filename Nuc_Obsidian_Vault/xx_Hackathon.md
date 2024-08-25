
# Roboflow Website
1. Create Project + workspace and follow [this video](https://blog.roboflow.com/getting-started-with-roboflow/) 
2. Go to "Upload Data" and upload training data set
3. Go to "Annotate" and start annotating some images



Training AI:
1. Use YOLOv8 using Roboflow
2. Use Object Detection mode
	1. Upload images
	2. Annotate images:
		1. Draw bounding boxes around potholes and classify as "potholes"
		2. Use custom bounding box to draw box around sticks and classify as "sticks"
	3. Go to generate:
		1. Apply following Pre-processing Steps (Make model more robust):
			1. ...
			2. ...
			3. ...
		2. Apply following Augmentations(Make model more robust):
			1. ...
			2. ...
			3. ...
		3. Train model
	4. Use following data from roboflow to perform pothole and stick detection in colab:
```Shell
%env ROBOFLOW_API_KEY=70zxvXOP1DUpvcvdtWrh
model = inference.get_model("stick2/1")
```




Google Colab for Testing model [here](https://colab.research.google.com/drive/1SuWfPclVmIW1vS6wnboHkvWyrxseXenV#scrollTo=2g9ROt4B_ypH):
1. For each image in directory do:
	1. Read Image
	2. Infer image
	3. find image height and width for normalisation
	4. clear .txt file
	5. separate inferred predictions into potholes and sticks
		1. For pothole detections do:
			1. take detected pothole bounding box
			2. normalise over image size
			3. save normalized values in .txt file
			4. denormalize dimension to draw the bounding box
			5. draw bounding box in specified colour
		2. For stick detections do:
			1. take detected stick bounding box
			2. normalise over image size
			3. save normalized values in .txt file
			4. denormalize dimension to draw the bounding box
			5. draw bounding box in specified colour
			5. go to next stick
	6. Display image with bounding boxes
