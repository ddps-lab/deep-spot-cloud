library(hash)
library(forecast)

set.seed(Sys.time()+Sys.getpid())

ondemand_price <- hash()
ondemand_price[["us-west-2"]] = 0.65
ondemand_price[["us-west-1"]] = 0.702
ondemand_price[["us-east-1"]] = 0.65
ondemand_price[["ap-northeast-1"]] = 0.898
ondemand_price[["ap-southeast-1"]] = 1.0
ondemand_price[["ap-southeast-2"]] = 0.898
ondemand_price[["eu-central-1"]] = 0.772
ondemand_price[["eu-west-1"]] = 0.702

getG2OndemandPrice <- function(filename) {
  region = convertFileNameToRegion(filename)
  type = getInstanceType(filename)
  ifelse(type=="g2.2xlarge", get(region,ondemand_price), get(region,ondemand_price)*4)
}

getInstanceType <- function(filename) {
  dir_sep = strsplit(filename, "/")[[1]]
  dir_sep = dir_sep[length(dir_sep)]
  strsplit(dir_sep, "_")[[1]][2]
}

convertFileNameToRegion <- function (filename) {
  dir_sep = strsplit(filename, "/")[[1]]
  dir_sep = dir_sep[length(dir_sep)]
  az = strsplit(dir_sep, "_")[[1]][1]
  substr(az, 1, nchar(az)-1) 
}

readAsTimeseries <- function(filename) {
  ondemand_price = getG2OndemandPrice(filename)
  price = read.table(filename)$V2
  price = price[-1]
  price = price[-length(price)]
  time_series = ts(sapply(price, function(x) min(1.0,x/ondemand_price)), frequency = 24)
  time_series
}

loadHourlyDataToTimeSeries <- function(directory_path) {
  forecast_arima <- hash()
  all_time_series = buildAllTimeSeries(directory_path)
  ts_names = names(all_time_series)
  for(name in ts_names) {
    time_series = all_time_series[[name]]
    .set(forecast_arima, name, hash())
    tryCatch({
      print("all")
      fit = auto.arima(time_series)
      print(fit)
      .set(get(name, forecast_arima), "all", fit)
      for(i in seq(31,182,30)) {
        fit = auto.arima(window(time_series,start=c(i,1)))
        print(i)
        print(fit)
        .set(get(name, forecast_arima),as.character(i),fit)
      }
    }, error=function(e) print(e))
  }
  forecast_arima
}

generateTestTimeWindow <- function(time_series) {
  test_start_day <- 120
  freq = frequency(time_series)
  total_days = as.integer(length(time_series)/freq)-2
  time_span = total_days - test_start_day
  test_end_day = test_start_day+as.integer(runif(1,0,time_span))
  test_hour = as.integer(runif(1,0,24))
  test_data=list()
  test_data[["predict"]] = window(time_series, start=c(1,1), end=c(test_end_day,test_hour))
  test_data[["eval"]] = window(time_series, start=c(1, 1), end=c(test_end_day+1,test_hour))
  test_data
}

generateTestTime <- function(time_series, day, time) {
  freq = frequency(time_series)
  test_data=list()
  test_data[["predict"]] = window(time_series, start=c(1,1), end=c(day, time))
  
}

buildAllTimeSeries <- function(directory) {
  all_timeseries <- list()
  fnames <- list.files(directory) 
  for (fn in fnames) {
    full_path = paste(directory,"/",fn,sep="")
    all_timeseries[[fn]] = readAsTimeseries(full_path)
  }
  all_timeseries
}

buildTestData <- function(all_time_series, all_arima) {
  types = names(all_arima)
  for (t in types) {
    print(t)
    test_times <- generateTestTimeWindow(all_time_series[[t]])
    arima_model = all_arima[[t]][["all"]]
    printAccuracy("stlf", accuracy(forecast(test_times[["predict"]], 24), test_times[["eval"]]))
    printAccuracy("arima", accuracy(forecast(test_times[["predict"]], 24, model=arima_model), test_times[["eval"]]))
    printAccuracy("snaive", accuracy(snaive(test_times[["predict"]], 24), test_times[["eval"]]))
    printAccuracy("meanf", accuracy(meanf(test_times[["predict"]], 24), test_times[["eval"]]))
    printAccuracy("rwf", accuracy(rwf(test_times[["predict"]], 24), test_times[["eval"]]))
  }
}

printAccuracy <- function(type, outcome) {
  print(paste(type, "train", outcome[3], "test", outcome[4]))
}

getRmseThroughTime <- function(time_series, start_day, end_day, method, arima=NULL) {
  test_rmse <- vector(length=(end_day-start_day)*24)
  train_rmse <- vector(length=(end_day-start_day)*24)
  eval_period = 12
  for(i in seq(start_day, end_day)) {
    for(j in seq(0, 23)) {
      test_time = window(time_series, start=c(1,1), end=c(i,j))
      eval_time = window(time_series, start=c(1,1), end=c(i+1,j))
      if(method == "naive") {
        total_acc = accuracy(rwf(test_time, eval_period), eval_time)
      } else if(method == "snaive") {
        total_acc = accuracy(snaive(test_time, eval_period), eval_time)
      } else if(method == "meanf") {
        test_time = window(time_series, start=c(i-7,j), end=c(i,j))
        total_acc = accuracy(meanf(test_time, eval_period), eval_time)
      } else if(method =="stlf") {
        total_acc = accuracy(forecast(test_time, eval_period), eval_time)
      } else if(method == "arima") {
        total_acc = accuracy(forecast(test_time, eval_period, model=arima), eval_time)
      }
      vec_index = (i-start_day) * 24 + j
      test_rmse[vec_index] = total_acc[4]
      train_rmse[vec_index] = total_acc[3]
    }
  }
  print(paste(method, "train", mean(train_rmse), "test", mean(test_rmse)))
  test_rmse
}

runAllTest <- function(all_time_series, all_arima) {
  regions = names(all_time_series)
  for (r in regions) {
    print(r)
    getRmseThroughTime(all_time_series[[r]], 120, 220, "naive")
    getRmseThroughTime(all_time_series[[r]], 120, 220, "snaive")
    getRmseThroughTime(all_time_series[[r]], 120, 220, "meanf")
    getRmseThroughTime(all_time_series[[r]], 120, 220, "stlf")
    getRmseThroughTime(all_time_series[[r]], 120, 220, "arima", all_arima[[r]][["all"]])
    gc()
  }
}

