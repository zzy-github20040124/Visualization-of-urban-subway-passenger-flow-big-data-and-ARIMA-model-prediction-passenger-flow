import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
import itertools
import matplotlib

# 设置非GUI后端
matplotlib.use('Agg')  # 在创建任何图形之前设置

# 1. 数据加载与预处理
def predict(site):
    path = "data\site_date\\" + site + '.xls'
    print("path : " + path)
    df = pd.read_excel(path, parse_dates=['日期'], index_col='日期')

    # 2. 观察时序图和自相关图
    plt.figure(figsize=(12, 6))

    plt.subplot(2, 1, 1)
    df['销量'].plot()

    title_fontprops = matplotlib.font_manager.FontProperties(family='SimHei')
    axis_fontprops = matplotlib.font_manager.FontProperties(family='SimHei')

    #plt.title('销量时序图',fontproperties=title_fontprops)

    plt.subplot(2, 1, 2)
    plot_acf(df['销量'].dropna(), lags=30)
    plt.title('自相关图',fontproperties=title_fontprops)

    plt.tight_layout()

    # 保存时序图和自相关图
    plt.savefig("static/time_series_and_acf.png")

    # 3. 定义网格搜索参数范围（扩大q值搜索范围以增加波动性）
    p_values = range(0, 4)  # 可根据实际情况调整范围
    d_values = range(0,2)  # 可根据实际情况调整范围
    q_values = range(0, 16)

    aic_min = float('inf')  # 初始化最小AIC值
    best_order = None  # 初始化最优参数组合

    for order in itertools.product(p_values, d_values, q_values):
        p, d, q = order

        try:
            model = ARIMA(df['销量'], order=(p, d, q))
            model_fit = model.fit()

            # 选择AIC作为评价指标
            aic = model_fit.aic
            if aic < aic_min:
                aic_min = aic
                best_order = order

        except Exception as e:
            print(f"Skipped order {order} due to error: {e}")

    print(f"Best ARIMA order found: {best_order} with AIC={aic_min}")

    # 5. 使用最优参数构建ARIMA模型并拟合数据
    p, d, q = best_order
    model = ARIMA(df['销量'], order=(p, d, q))
    model_fit = model.fit()

    # 6. 模型诊断（可选）
    print(model_fit.summary())

    # 保存残差自相关图
    plt.figure(figsize=(12, 6))
    plot_acf(model_fit.resid, ax=plt.gca())
    plt.title('残差自相关',fontproperties=title_fontprops)
    plt.savefig("static/residuals_acf.png")

    # 7. 预测未来数据
    forecast_periods = 15  # 预测期数
    forecast = model_fit.get_forecast(steps=forecast_periods)

    # 8. 获取预测结果、置信区间
    forecast_mean = forecast.predicted_mean
    forecast_conf_int = forecast.conf_int()
    forecast_ci_upper = forecast_conf_int.iloc[:, 1]
    forecast_ci_lower = forecast_conf_int.iloc[:, 0]


    # 绘制预测结果
    plt.figure(figsize=(12, 6))
    df['销量'].plot(label='实际销量数据线')
    forecast_mean.plot(label='预测销量数据及置信区间', color='r', linestyle='--')
    plt.fill_between(forecast_ci_lower.index, forecast_ci_lower, forecast_ci_upper, alpha=0.2, color='pink')

    # 设置轴标签和图例，使用指定的字体属性
    plt.xlabel('时间', fontproperties=axis_fontprops)
    plt.ylabel('销量', fontproperties=axis_fontprops)
    plt.legend(prop={'family': 'SimHei'}, framealpha=1)  # 设置图例字体和边框

    plt.title(site + '站大数据时序销量预测模型图', fontproperties=title_fontprops)

    s = "static/ail.png"
    plt.savefig(s)

    return s