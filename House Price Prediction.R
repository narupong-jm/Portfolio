library(tidyverse)
library(readxl)
library(caret)
library(rpart)
library(rpart.plot)

# Read excel to dataset
dataset = tibble(read_excel('/Users/j.nrup/Documents/Data Project/House Price India.xlsx'))
head(dataset)

# Check null
if (mean(complete.cases(dataset)) != 1) {
  # Delete null.
  clean_data <- drop_na(dataset)
  print("Remove null completely!")
  mean(complete.cases(clean_data))
} else {
  clean_data <- dataset
  print("Data was clean!")
}

clean_data <- clean_data[, !(names(clean_data) %in% c("id","Date","Built Year","Renovation Year","Postal Code","Lattitude","Longitude"))]
clean_data

col_name_mappings <- c(
  "number of bedrooms" = "no_of_bedrooms",
  "number of bathrooms" = "no_of_bathrooms",
  "living area" = "living_area",
  "lot area" = "lot_area",
  "number of floors" = "no_of_floors",
  "waterfront present" = "waterfront",
  "number of views" = "no_of_views",
  "condition of the house" = "condition_house",
  "grade of the house" = "grade_house",
  "Area of the house(excluding basement)" = "area_house",
  "Area of the basement" = "area_basement",
  "living_area_renov" = "living_renov",
  "lot_area_renov" = "lot_renov",
  "Number of schools nearby" = "no_of_schools_nearby",
  "Distance from the airport" = "distance_airport",
  "Price" = "price"
)

# Rename columns using the mappings
colnames(clean_data) <- sapply(colnames(clean_data), function(col) col_name_mappings[col])
clean_data

ggplot(data = clean_data, mapping = aes(x = price)) + 
  geom_histogram(bins=30, fill = "#F5AD9E") + 
  labs(title = "Distribution of House Price") + 
  theme_minimal()

# Apply a log transformation
data_lm <- clean_data %>%
  mutate(log_price = log(price))
data_lm

ggplot(data=data_lm, mapping = aes(x=log_price)) +
         geom_histogram(bin=30, fill = "#D9F588") +
         labs(title = "Distribution of Log price") +
         theme_minimal()

# Split data
split_func <- function(data, train_size = 0.8) {
  set.seed(42)
  n <- nrow(data)
  id <- sample(1:n,size = n*train_size)
  train_data <- data[id, ]
  test_data <- data[-id, ]
  list(train = train_data, test = test_data)
}

pre_data <- split_func(data_lm)

trainData <- pre_data[[1]]
testData <- pre_data[[2]]

# Train Model
set.seed(40)
lmModel <- train(log_price ~ . - price,
                  data = trainData,
                  method = "lm")
lmModel

print("Regression Equation: ") 
lmModel$finalModel
# significant
varImp(lmModel)   

# Evaluate Model                               
# Score Model; Predict Unseen data
pTrain_LM <- predict(lmModel, newdata = trainData)
unlog_pTrain_LM <- exp(pTrain_LM)
pTest_LM <- predict(lmModel, newdata = testData)
unlogpTest_LM <- exp(pTest_LM)                               

# Create Function to calculate MAE
calcu_mae <- function(actual, pred) {
  error <- actual - pred
  return(mean(abs(error)))
  }
# Create Function to calculate MSE
  calcu_mse <- function(actual, pred) {
    error <- actual - pred
    return(mean(error**2))
  }

# Create Function to calculate RMSE
calcu_rmse <- function(actual, pred) {
  error <- actual - pred
  return(sqrt(mean(error**2)))
}

MAETrain <- calcu_mae(trainData$price, unlog_pTrain_LM)
MAETest <- calcu_mae(testData$price, unlogpTest_LM)
MSETrain <- calcu_mse(trainData$price, unlog_pTrain_LM)
MSETest <- calcu_mse(testData$price, unlogpTest_LM)
RMSETrain <- calcu_rmse(trainData$price, unlog_pTrain_LM)
RMSETest <- calcu_rmse(testData$price, unlogpTest_LM)

result <- c("MAE", "MSE", "RMSE")
Train <- c(MAETrain, MSETrain, RMSETrain)
Test <- c(MAETest, MSETest, RMSETest)

result_df <- data.frame(result,Train, Test)
result_df


# - Algorithm : Regularized Regression
# - Re-sampling Technique : K-Fold Cross Validation (Create Train control to setting condition of train process.)
# - Hyper-parameter tuning : Create my_grid to Hyper-parameter tuning process. 

## create train control
set.seed(42)
ctrl_cv <- trainControl(method = "cv",
                        number = 8,
                        verboseIter = TRUE)
## create my_grid
my_grid <- expand.grid(alpha = 0:1,
                       lambda = seq(0.0005, 0.05, length = 20))
## train model
glmModel_cv <- train(log_price ~ . - price,
                     data = trainData,
                     method = "glmnet",
                     tuneGrid = my_grid,
                     trControl = ctrl_cv)
print("Regularized Regression with K-Fold Cross Validation")
print(glmModel_cv)

## Predict Unseen data
pTrain_glm_cv <- predict(glmModel_cv, newdata = trainData)
unlog_pTrain_glm_cv <- exp(pTrain_glm_cv)
pTest_glm_cv <- predict(glmModel_cv, newdata = testData)
unlog_pTest_glm_cv <- exp(pTest_glm_cv)

MAETrain_glm_cv <- calcu_mae(trainData$price, unlog_pTrain_glm_cv)
MAETest_glm_cv <- calcu_mae(testData$price, unlog_pTest_glm_cv)
MSETrain_glm_cv <- calcu_mse(trainData$price, unlog_pTrain_glm_cv)
MSETest_glm_cv <- calcu_mse(testData$price, unlog_pTest_glm_cv)
RMSETrain_glm_cv <- calcu_rmse(trainData$price, unlog_pTrain_glm_cv)
RMSETest_glm_cv <- calcu_rmse(testData$price, unlog_pTest_glm_cv)

RMSE_of_glmnet <- c("MAE","MSE","RMSE")
Train_glmnet <- c(MAETrain_glm_cv,MSETrain_glm_cv,RMSETrain_glm_cv)
Test_glmnet <- c(MAETest_glm_cv,MSETest_glm_cv,RMSETest_glm_cv)

RMSE_of_glmnet_df <- data.frame(RMSE_of_glmnet,Train_glmnet, Test_glmnet)
RMSE_of_glmnet_df       

# - Algorithm : Decision Tree
# - Re-sampling Technique : K-Fold Cross Validation
# - Hyper-parameter tuning
## create train control
set.seed(42)
ctrl_tree <- trainControl(method = "cv",
                          number = 8,
                          verboseIter = TRUE)
## train model
tree_model <- train(log_price ~ . - price,
                    data = trainData,
                    method = "rpart",
                    tuneGrid = expand.grid(cp = c(0.02,0.1,0.25)),
                    trControl = ctrl_tree)
print("Decision Tree Model with K-Fold Cross Validation")
print(tree_model)
                               
## Decision Tree Model Visualization
rpart.plot(tree_model$finalModel)

## Predict Unseen data
pTrain_tree_cv <- predict(tree_model, newdata = trainData)
unlog_pTrain_tree_cv <- exp(pTrain_tree_cv)
pTest_tree_cv <- predict(tree_model, newdata = testData)
unlog_pTest_tree_cv <- exp(pTest_tree_cv)

MAETrain_tree_cv <- calcu_mae(trainData$price, unlog_pTrain_tree_cv)
MAETest_tree_cv <- calcu_mae(testData$price, unlog_pTest_tree_cv)
MSETrain_tree_cv <- calcu_mse(trainData$price, unlog_pTrain_tree_cv)
MSETest_tree_cv <- calcu_mse(testData$price, unlog_pTest_tree_cv)
RMSETrain_tree_cv <- calcu_rmse(trainData$price, unlog_pTrain_tree_cv)
RMSETest_tree_cv <- calcu_rmse(testData$price, unlog_pTest_tree_cv)

RMSE_of_tree <- c("MAE","MSE","RMSE")
Train_tree <- c(MAETrain_tree_cv,MSETrain_tree_cv,RMSETrain_tree_cv)
Test_tree <- c(MAETest_tree_cv,MSETest_tree_cv,RMSETest_tree_cv)

RMSE_of_tree_df <- data.frame(RMSE_of_tree,Train_tree, Test_tree)
RMSE_of_tree_df

# - Algorithm : Random forest and Neural network
# - Re-sampling Technique : K-Fold Cross Validation
# - Hyper-parameter tuning
set.seed(42)
ctrl_rf_nn <- trainControl(method = "cv",
                           number = 5,
                           verboseIter = TRUE)
rf_mod <- train(log_price ~ . - price,
                data = trainData,
                method = "rf",
                tuneLength = 5,
                trControl = ctrl_rf_nn)
nn_mod <- train(log_price ~ . - price,
                data = trainData,
                method = "nnet",
                tuneLength = 5,
                trControl = ctrl_rf_nn)
print("Random Forest Model with K-Fold Cross Validation")
print(rf_mod)
print("Neural Network Model with K-Fold Cross Validation")
print(nn_mod)

## Predict Unseen data
pTrain_rf_cv <- predict(rf_mod, newdata = trainData)
unlog_pTrain_rf_cv <- exp(pTrain_rf_cv)
pTest_rf_cv <- predict(rf_mod, newdata = testData)
unlog_pTest_rf_cv <- exp(pTest_rf_cv)

pTrain_nn_cv <- predict(nn_mod, newdata = trainData)
unlog_pTrain_nn_cv <- exp(pTrain_nn_cv)
pTest_nn_cv <- predict(nn_mod, newdata = testData)
unlog_pTest_nn_cv <- exp(pTest_nn_cv)

MAETrain_rf_cv <- calcu_mae(trainData$price, unlog_pTrain_rf_cv)
MAETest_rf_cv <- calcu_mae(testData$price, unlog_pTest_rf_cv)
MSETrain_rf_cv <- calcu_mse(trainData$price, unlog_pTrain_rf_cv)
MSETest_rf_cv <- calcu_mse(testData$price, unlog_pTest_rf_cv)
RMSETrain_rf_cv <- calcu_rmse(trainData$price, unlog_pTrain_rf_cv)
RMSETest_rf_cv <- calcu_rmse(testData$price, unlog_pTest_rf_cv)

MAETrain_nn_cv <- calcu_mae(trainData$price, unlog_pTrain_nn_cv)
MAETest_nn_cv <- calcu_mae(testData$price, unlog_pTest_nn_cv)
MSETrain_nn_cv <- calcu_mse(trainData$price, unlog_pTrain_nn_cv)
MSETest_nn_cv <- calcu_mse(testData$price, unlog_pTest_nn_cv)
RMSETrain_nn_cv <- calcu_rmse(trainData$price, unlog_pTrain_nn_cv)
RMSETest_nn_cv <- calcu_rmse(testData$price, unlog_pTest_nn_cv)

RMSE_of_rf <- c("MAE","MSE","RMSE")
Train_rf <- c(MAETrain_rf_cv,MSETrain_rf_cv,RMSETrain_rf_cv)
Test_rf <- c(MAETest_rf_cv,MSETest_rf_cv,RMSETest_rf_cv)

RMSE_of_nn <- c("MAE","MSE","RMSE")
Train_nn <- c(MAETrain_nn_cv,MSETrain_nn_cv,RMSETrain_nn_cv)
Test_nn <- c(MAETest_nn_cv,MSETest_nn_cv,RMSETest_nn_cv)

RMSE_of_rf_df <- data.frame(RMSE_of_rf,Train_rf, Test_rf)
RMSE_of_nn_df <- data.frame(RMSE_of_nn,Train_nn, Test_nn)

print(RMSE_of_rf_df)
print(RMSE_of_nn_df)

# Comparison Model with RMSE                               
comparision <- c("Linear Regression", "Regularized Regression", "Decision Tree", "Random Forest", "Neural Network")
train_rmse <- c(RMSETrain, RMSETrain_glm_cv, RMSETrain_tree_cv, RMSETrain_rf_cv, RMSETrain_nn_cv)
test_rmse <- c(RMSETest, RMSETest_glm_cv, RMSETest_tree_cv, RMSETest_rf_cv, RMSETest_nn_cv)

diff_lm <- abs(RMSETrain-RMSETest)
diff_glmnet <- abs(RMSETrain_glm_cv-RMSETest_glm_cv)
diff_tree <- abs(RMSETrain_tree_cv-RMSETest_tree_cv)
diff_rf <- abs(RMSETrain_rf_cv-RMSETest_rf_cv)
diff_nn <- abs(RMSETrain_nn_cv-RMSETest_nn_cv)
Difference <- c(diff_lm, diff_glmnet, diff_tree, diff_rf, diff_nn)

com_model <- data.frame(comparision, train_rmse, test_rmse,Difference)
print(com_model)

## save model .RDS
saveRDS(nn_mod, "/Users/j.nrup/Documents/Data Project/nn_model.RDS")







                               
