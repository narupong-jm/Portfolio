library(tidyverse)
library(RPostgreSQL)
library(DBI)
library(ggplot2)
library(patchwork)

df <- read_csv("housePriceInBangkok.csv")

# [1] connect to database.
con <- dbConnect(PostgreSQL(),
                 host = "floppy.db.elephantsql.com", # Server
                 port = 5432, # Door to the room // default in postgreSQL: 5432
                 user = "xjyjkkgf",
                 password = "psJ6nkYIx0qJVO6IUjVpnjitAhgHYNnr",
                 dbname = "xjyjkkgf") # default database

# [2] Check table list.
cat("List table in database : ", dbListTables(con))

# [3] Remove table if it exist and write table to database.
# Check if the table exists.
if (dbExistsTable(con, "housePrice")) {
  # If it exists, remove the table.
  dbRemoveTable(con, "houseprice")
  print("houseprice removed successfully.")
} 
# write new table.
dbWriteTable(con, "houseprice", df)
print("houseprice write completely.")

# [4] Get data
dbGetQuery(con, "SELECT title, location, beds, baths, usable_area, land_area, floors
FROM houseprice
LIMIT 10;")

cat("List table in database : ", dbListTables(con))

# [5] Close connection
dbDisconnect(con)

housePrice_df <- tibble(df)
head(housePrice_df)

# Check null row.
mean(complete.cases(housePrice_df))

# Delete null.
clean_df <- drop_na(housePrice_df)
mean(complete.cases(clean_df))

# Change Column name to snake case.
column_name_mappings <- c(
  "...1" = "no",
  "title" = "title",
  "location" = "location",
  "price" = "price",
  "beds" = "beds",
  "baths" = "baths",
  "usable_area" = "usable_area",
  "land_area" = "land_area",
  "floors" = "floors",
  "Access for the disabled" = "access_for_the_disabled",
  "Air conditioning" = "air_conditioning",
  "Alarm" = "alarm",
  "Balcony" = "balcony",
  "Built-in kitchen" = "built_in_kitchen",
  "Built-in wardrobe" = "built_in_wardrobe",
  "Car park" = "car_park",
  "Cellar" = "cellar",
  "Children's area" = "children_area",
  "Cistern" = "cistern",
  "Concierge" = "concierge",
  "Electricity" = "electricity",
  "Elevator" = "elevator",
  "Equipped kitchen" = "equipped_kitchen",
  "Fireplace" = "fireplace",
  "Garden" = "garden",
  "Grill" = "grill",
  "Guardhouse" = "guardhouse",
  "Gym" = "gym",
  "Hot Tub" = "hot_tub",
  "Internet" = "internet",
  "Library" = "library",
  "Natural gas" = "natural_gas",
  "Office" = "office",
  "Panoramic view" = "panoramic_view",
  "Patio" = "patio",
  "Roof garden" = "roof_garden",
  "Sauna" = "sauna",
  "Security" = "security",
  "Swimming pool" = "swimming_pool",
  "Tennis court" = "tennis_court",
  "Terrace" = "terrace",
  "Utility room" = "utility_room",
  "Video cable" = "video_cable",
  "Water" = "water"
)

# Rename columns using the mappings
colnames(clean_df) <- sapply(colnames(clean_df), function(col) column_name_mappings[col])
clean_df

ggplot(data = clean_df, mapping = aes(x = price)) + 
  geom_histogram(bins=30, fill = "#F5AD9E") + 
  labs(title = "Distribution of House Price") + 
  theme_minimal()

ggplot(data = clean_df, mapping = aes(x = price)) + 
  geom_boxplot() + 
  labs(title = "Outlier detection of House Price") + 
  theme_minimal()  

out <- boxplot.stats(clean_df$price)$out
out                        

out_ind <- which(clean_df$price %in% c(out))
out_ind

clean_df[out_ind, ]

clean_dfNo_out <- clean_df[-out_ind,]
clean_dfNo_out

ggplot(data = clean_dfNo_out, mapping = aes(x=usable_area, y=price, col=price)) + 
  geom_point() + 
  labs(title = "usable_area vs price") +
  scale_color_gradient(low="gold",high = "blue")

c1 <- ggplot(data = clean_df, mapping = aes(x = price)) + 
  geom_histogram(bins=10, fill = "#F5AD9E") + 
  labs(title = "Distribution of House Price") + 
  theme_minimal()

c2 <- ggplot(data = clean_df, mapping = aes(x = price)) + 
  geom_boxplot() + 
  labs(title = "Outlier Detection of House Price") + 
  theme_minimal()

c3 <- ggplot(data = clean_dfNo_out, mapping = aes(x=usable_area, y=price, col=price)) + 
  geom_point() + 
  labs(title = "usable_area vs price") +
  scale_color_gradient(low="gold",high = "blue")

(c1 + c2)/c3

# Select specific variables for the correlation matrix
selected_vars <- c("price", "beds", "baths", "usable_area", "land_area", "floors")

# Create a correlation matrix for the selected variables
cor_matrix_selected <- round(
  cor(clean_dfNo_out[, selected_vars]),
  digits = 2
)

# Print the correlation matrix for selected variables
print(cor_matrix_selected)

# improved correlation matrix
library(corrplot)

corrplot(cor_matrix_selected,
  method = "number",
  type = "upper" # show only upper side
)                             


                             
