# Retrieves stock data for multiple tickers, and plots a single ticker with indicators as entered.
# Not all indicators are supported. Currently: ADX, MACD, RSI, SMA, and BBands.
# Split into more functions than necessary for cutting/pasting. 

library(TTR)
library(xts)
library(quantstrat)
library(quantmod)

#----------------------------------------------------------------------------------------#

main <- function () {
collectSubsetDates()
collectSymbols()
plotChart()
}

#----------------------------------------------------------------------------------------#

# Get today's date and get the start and end dates of the subset.
collectSubsetDates <- function () { 
    today <- assign('today', Sys.Date(), globalenv()
    subset_start <- assign('subset_start', readline(prompt = paste0("Enter start date (yyyy-mm-dd) [", as.Date(today)-365, "]: ")), globalenv())
    if(subset_start == "") {
        subset_start <- assign('subset_start', as.Date(today)-365, globalenv())
    }
    subset_end <- assign('subset_end', readline(prompt = paste0("Enter end date (yyyy-mm-dd) [", as.Date(today), "]: ")), globalenv())
    if(subset_end == "") {
        subset_end <- assign('subset_end', as.Date(today), globalenv())
    }
    ticker_subset <- assign('ticker_subset', paste0(subset_start, "::", subset_end), globalenv())
}

#----------------------------------------------------------------------------------------#

# Get symbols for open and close data. Can be edited to change the data output
collectSymbols <- function () {
    symbol_count <- assign('symbol_count', 1, globalenv())
    symbol_default <- assign('symbol_default', "NVDA", globalenv()) 
    symbol <- symbol_default
    symbol_list <- assign('symbol_list', NULL, globalenv())
    while(symbol != "") {
        if(symbol_count == 1) {
            symbol <- readline(prompt = paste0("Enter Ticker (enter to stop)[", symbol_default,"]: "))
        } else {
            symbol <- readline(prompt = "Enter Ticker (enter to stop): ")
        }
        if(symbol != "") {
            symbol_list <- assign('symbol_list', c(symbol_list, symbol), globalenv())
            symbol_count <- assign('symbol_count', symbol_count + 1, globalenv())
        }
        if(symbol == "" && symbol_count == 1) {
            symbol_list <- assign('symbol_list', symbol_default, globalenv())
            symbol_count <- assign('symbol_count', symbol_count + 1, globalenv())
        }
    }
    getSymbols(symbol_list, src = "yahoo", from = subset_start, to = subset_end, auto.assign = TRUE)
    i <- 1
    # Edit this for different data output
    while (i < symbol_count) {
        temp <- get(symbol_list[i])
    #    print(summary(temp[,4]))
        print(paste0("Open: ", 
              format(round(Op(to.period(temp, period="weeks")), digits=2), nsmall=2), 
              " Close: ", 
              format(round(Cl(to.period(temp, period="weeks")), digits=2), nsmall=2)))
        i <- i + 1
    }
}

#----------------------------------------------------------------------------------------#

# Charts the symbol entered and runs the collected indicator functions
plotChart <- function() {
    chart_symbol <- readline(prompt = paste0("Symbol to chart [", symbol_list[1], "] : "))
    if(chart_symbol == "") {
        chart_symbol <- assign('chart_symbol', symbol_list[1], globalenv())
    }
    getSymbols(chart_symbol, src = "yahoo", from = subset_start, to = subset_end, auto.assign = TRUE)
    linetype <- readline(prompt = "Linetype (auto, candlesticks, matchsticks, bars, line): [candlesticks]: ")
    if(linetype == "") {
        linetype <- "candlesticks"
    }
    up_color <- "green"
    down_color <- "red"
    theme_color <- "black"
    show_grid <- TRUE
    chartSeries(get(chart_symbol),
                name = chart_symbol,
                type = linetype, 
                subset = ticker_subset, 
                up.col = up_color, 
                dn.col = down_color, 
                theme = theme_color, 
                show.grid = show_grid)
    volume_on_off <- readline(prompt = "Volume On? (y/n): ")
    if(volume_on_off == "") {
        volume_on_off <- "y"
    }
    if(volume_on_off == "n") {
        dropTA('addVo')
    }
    indicatorCollector()
    SMA_count <- assign('SMA_count', 0, globalenv())
    if (indicator_list[1] != "") {
        i <- 0
        while(i < indicator_count) {
            print(indicator_list[i + 1])
            eval(parse(text = paste0(indicator_list[i + 1], "()")))
            i = i + 1
        }
    }
}

#----------------------------------------------------------------------------------------#

indicatorCollector <- function() {
    indicator_count <- assign('indicator_count', 0, globalenv())
    indicator_list <- assign('indicator_list', NULL, globalenv())
    temp_indicator <- "MACD"
    while(temp_indicator != "") {
        temp_indicator <- readline(prompt = "Enter Indicator (enter to stop): ")
        if(temp_indicator != "") {
            indicator_list <- assign('indicator_list', c(indicator_list, temp_indicator), globalenv())
            indicator_count <- assign('indicator_count', indicator_count + 1, globalenv())
        }
        if(temp_indicator == "" && indicator_count == 0) {
            indicator_list <- assign('indicator_list', NULL, globalenv())
        }
    }
}

#----------------------------------------------------------------------------------------#

MACD <- function () {
    MACD_fast_default <- 12
    MACD_slow_default <- 26
    MACD_signal_default <- 9
    MACD_type_default <- "EMA"
    MACD_fast <- readline(prompt = paste0("Fast: [", MACD_fast_default,"]: "))
    if(MACD_fast == "") {
        MACD_fast <- MACD_fast_default
    }
    MACD_slow <- readline(prompt = paste0("Slow: [", MACD_slow_default,"]: "))
    if(MACD_slow == "") {
        MACD_slow <- MACD_slow_default
    }
    MACD_signal <- readline(prompt = paste0("Signal: [", MACD_signal_default,"]: "))
    if(MACD_signal == "") {
        MACD_signal <- MACD_signal_default
    }
    MACD_type <- readline(prompt = paste0("Type: [", MACD_type_default,"]: "))
    if(MACD_type == "") {
        MACD_type <- MACD_type_default
    }
    plot(addMACD(fast = as.numeric(MACD_fast), slow = as.numeric(MACD_slow), signal = as.numeric(MACD_signal), type = MACD_type))
}

#----------------------------------------------------------------------------------------#

ADX <- function () {
    period_default <- 14
    ma_type_default <- "EMA"
    period <- readline(prompt = paste0("Period Numbers: [", period_default,"]: "))
    if(period == "") {
        period <- period_default
    }
    ma_type <- readline(prompt = paste0("Moving Average Type: [", ma_type_default,"]: "))
    if(ma_type == "") {
        ma_type <- ma_type_default
    }
    plot(addADX(n = as.numeric(period), maType = ma_type))
}

#----------------------------------------------------------------------------------------#

RSI <- function () {
    period_default <- 14
    ma_type_default <- "EMA"
    period <- readline(prompt = paste0("Period Numbers: [", period_default,"]: "))
    if(period == "") {
        period <- period_default
    }
    ma_type <- readline(prompt = paste0("Moving Average Type: [", ma_type_default,"]: "))
    if(ma_type == "") {
        ma_type <- ma_type_default
    }
    plot(addRSI(n = as.numeric(period), maType = ma_type))
}

#----------------------------------------------------------------------------------------#

Volume <- function () {
    plot(addVo())
}

#----------------------------------------------------------------------------------------#

BBands <- function () {
    period_default <- 12
    standard_deviation_default <- 2
    ma_type_default <- "SMA"
    draw_default <- "bands"
    period <- readline(prompt = paste0("Period Numbers: [", period_default,"]: "))
    if(period == "") {
        period <- period_default
    }
    standard_deviation <- readline(prompt = paste0("Standard Deviation: [", standard_deviation_default,"]: "))
    if(standard_deviation == "") {
        standard_deviation <- standard_deviation_default
    }
    ma_type <- readline(prompt = paste0("Moving Average Type: [", ma_type_default,"]: "))
    if(ma_type == "") {
        ma_type <- ma_type_default
    }
    draw_type <- readline(prompt = paste0("Draw (bands, percent, or width): [", draw_default,"]: "))
    if(draw_type == "") {
        draw_type <- draw_default
    }
    plot(addBBands(n = as.numeric(period), sd = standard_deviation, maType = ma_type, draw = draw_type))
}

#----------------------------------------------------------------------------------------#

SMA <- function () {
    period_default <- 10
    if (SMA_count == 0) {
    color_default <- "pink"
    }
    if (SMA_count == 1) {
    color_default <- "green"
    }
    if (SMA_count == 2) {
    color_default <- "blue"
    }
    if (SMA_count == 3) {
    color_default <- "black"
    }
    if (SMA_count > 3) {
    color_default <- "yellow"
    }
    period <- readline(prompt = paste0("Period Numbers: [", period_default,"]: "))
    if(period == "") {
        period <- period_default
    }
    color <- readline(prompt = paste0("Color: [", color_default,"]: "))
    if(color == "") {
        color <- color_default
    }
    SMA_count <- assign('SMA_count', SMA_count + 1, globalenv())
    plot(addSMA(n = as.numeric(period), col = color))    
}

#----------------------------------------------------------------------------------------#

main()

#----------------------------------------------------------------------------------------#
