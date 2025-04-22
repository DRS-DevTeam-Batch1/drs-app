# Trajectory Analysis Models for Decision Review System (DRS)

As part of our work on building a trajectory analysis module for a Decision Review System (DRS) in cricket, we explored different models used for predicting sequences.  
We are given a list of coordinates (the tracked path of the ball before the bounce), and our task is to predict the remaining path of the ball, especially after the bounce.

## 1. LSTM (Long Short-Term Memory)
We began with LSTM because it’s one of the standard models for time-series prediction. It’s good at learning patterns in sequences and was quite easy to implement.

### Pros:
- Understands time-based patterns naturally.
- Works fine with limited training data.
- Gives decent short-term predictions.

### Cons:
- Doesn’t “know” any physics, so the predictions can sometimes look unnatural.
- Not the best at handling long-term behavior like the ball's final dip or swing.

## 2. BiLSTM (Bidirectional LSTM)
Then we tried BiLSTM, which looks at both past and future data while making predictions. This gives it a better understanding of the full sequence.

### Pros:
- Learns both forward and backward time dependencies.
- Gave slightly better accuracy compared to regular LSTM in tests.

### Cons:
- Not practical for real-time systems since future data won’t always be available.
- Needs more computation.

## 3. GRU (Gated Recurrent Unit)
We also tried GRU, which is like a lighter version of LSTM. It’s faster and simpler but still effective in many cases.

### Pros:
- Quicker training and inference.
- Performs well on small datasets.

### Cons:
- Slightly less powerful when dealing with complex motion like sharp swing or spin.
- Like LSTM, it doesn’t include any real-world physics.

## 4. Transformer-based Time-Series Model
We looked into newer models like the TimeSeriesTransformer and Informer. These use attention mechanisms to focus on important points in the data.

### Pros:
- Very effective at learning long-term dependencies.
- Can model sudden changes, like a fast bounce or spin.

### Cons:
- Needs a large amount of data for training.
- High computational cost; maybe overkill for short ball sequences.

### Reference:
- [Informer paper](https://arxiv.org/abs/2012.07436)
- TimeSeriesTransformer on HuggingFace

## 5. Kalman Filter (with noise and spin handling)
This is a traditional method used in tracking systems. It uses equations of motion and adjusts predictions based on noise.

### Pros:
- Very precise when dealing with clean, slightly noisy data.
- Can estimate hidden values like velocity or spin.

### Cons:
- Doesn’t learn from past data—relies completely on mathematical models.
- Needs fine-tuning of parameters (like measurement noise).

### Reference:
- [Kalman filter explanation](https://www.kalmanfilter.net/)
- [Application in sports tracking](https://ieeexplore.ieee.org/document/7827584)

## 6. Physics-Informed Neural Networks (PINNs)
We found PINNs quite interesting because they mix deep learning with physical laws like gravity, air resistance, and the Magnus effect.

### Pros:
- Gives more realistic and interpretable predictions.
- Maintains consistency with physical rules.

### Cons:
- Needs good knowledge of cricket physics to build.
- Training takes longer and is harder to set up.

### Reference:
- [Physics-informed neural networks paper](https://arxiv.org/abs/2003.03485)

## 7. Hybrid LSTM + Physics-Based Model
Lastly, we experimented with a hybrid model. Here, LSTM learns the pattern from data, and then physics equations adjust the output to make it more realistic (e.g., to simulate bounce or swing properly).

### Pros:
- Combines the strengths of both machine learning and physics.
- Gave good results even with medium-sized datasets.
- Can realistically simulate post-bounce behavior.

### Cons:
- More complex to implement than just using LSTM alone.
- Needs tuning of physics-related variables like drag, bounce angle, and spin.

## Some additional models

## 8. Multivariate Linear Regression (MLR)

MLR fits a linear equation between multiple input features (e.g., time, x, y, z positions) and the target output.

**Pros:**  
- Very simple and interpretable  
-  fast to train and test  
- Works decently when ball motion is fairly linear

**Cons:**  
- Cannot model non-linear behaviors like bounce or swing  

## 9. Polynomial Regression

This extends linear regression by introducing polynomial terms to better fit curved data patterns.

**Pros:**  
- Can capture simple non-linear motion  
- Easy to implement

**Cons:**   
- Risk of overfitting with high-degree polynomials espescially since our dataset might not be large


## 10. Convolutional Neural Networks (CNNs)

 1D CNNs to learn local patterns in the ball's motion trajectory.

**Pros:**  
- Captures local variations (e.g., bounce, dip)  
- Efficient training and inference  
- Less likely to overfit than fully connected networks

**Cons:**  
- Not good at learning long-term dependencies  

## 11. Gaussian Process Regression (GPR)

GPR is a non-parametric regression method that provides uncertainty estimates along with predictions.

**Pros:**  
- Works well with small datasets  
- Provides smooth and continuous predictions  
- Includes uncertainty quantification

**Cons:**  
- Not scalable to large datasets (but might work in our case)
- Computationally expensive (but other models with high accuracy are same)

 ## Final Shortlisted Models

We shortlist a few models based on prediction quality, physics accuracy, implementation difficulty, and data availability.

### 1. Hybrid LSTM + Physics Model

This approach combines LSTM-based sequence learning with physics-based equations (gravity, drag, bounce, spin).

**Why:**  
- Captures time and real-world behavior  
- Can handle moderate-sized datasets effectively  
- Produces physically plausible bounce and spin

### 2. Kalman Filter

A probabilistic model that updates its predictions using noise models and physics equations.

**Why:**  
- Fast and lightweight  
- Very effective on smooth and noisy data (real world scenario like our case)
- No training required, can work in real-time

### 3. Physics-Informed Neural Networks (PINNs)

PINNs combine machine learning with physical laws during training to enforce physically consistent outputs.

**Why we selected it:**  
- Ensures predictions follow known physical laws  
- Produce more realistic results  
- Performs with limited data

  ### Note:
  Due to our limited data availablity (coordinates) and optional timestamps, we might have to consider stepping back from above advanced models and instead use Polynomial or Gaussian Regression. It will depend as we make progress in this project.
