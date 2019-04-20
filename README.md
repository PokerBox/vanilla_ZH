# OSU Intelligent Robot
OSU Robotmaster Machine Learning Library  

Reference: darknet (https://github.com/AlexeyAB/darknet)

# Intelligent Fire System

**Pipeline 1: High-speed Camera -> Image Processing -> Object Detection -> Position Correction -> Object Matching -> Signal Filtering 1 -> Motion Prediction -> Reinforcement Learning Controller -> Signal Filtering 2 -> ESC -> Motors**  
  
**Pipeline 2: Image Processing -> Dual camera -> Depth estimation -> Calculating the shell’s flying time**  
  
Image Processing: Enhance the lightness of video frames and do distortion correction using OpenCV  
  
Object Detection: Yolov3-tiny model with ~1,000 training images and ImageNet pre-trained model, achieve 30fps at 640p video and IOU ~90% on Jetson TX2 GPU  
  
Object Matching: Based on the logic of different objects’ location, match the bounding box among frames  
  
Position Correction: Add camera position to the bounding box, making the location of bounding box   
  
Signal Filtering 1: Kalman filter and smoothing function, making the bounding box stable and smooth  
  
Motion Prediction: Polynomial regression for vector based function, predicting the future trajectory  
  
Reinforcement Leaning Controller: Soft Actor-Critic algorithm. The shooting function as reward, position and speed as environment. Output the PWM average power.  
  
Signal Filtering 2: Kalman filter for signal interpolation and smoothing, increase the refresh frequency of control signal  

