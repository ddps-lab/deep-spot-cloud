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
