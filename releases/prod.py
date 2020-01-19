"""
#   Technical Analysis Tools
#
#   by: nga-27
#
#   A program that outputs a graphical and a numerical analysis of
#   securities (stocks, bonds, equities, and the like). Analysis 
#   includes use of oscillators (Stochastic, RSI, and Ultimate), 
#   momentum charting (Moving Average Convergence Divergence, 
#   Simple and Exponential Moving Averages), trend analysis (Bands, 
#   Support and Resistance, Channels), and some basic feature 
#   detection (Head and Shoulders, Pennants).
#   
"""

# Imports that are custom tools that are the crux of this program
from libs.tools import full_stochastic, ultimate_oscillator, cluster_oscs, RSI
from libs.tools import relative_strength, triple_moving_average, moving_average_swing_trade
from libs.tools import mov_avg_convergence_divergence, on_balance_volume
from libs.tools import beta_comparison
from libs.tools import find_resistance_support_lines
from libs.tools import get_trendlines, get_trend_analysis
from libs.tools import get_high_level_stats

# Imports that support functions doing feature detection
from libs.features import feature_detection_head_and_shoulders, feature_plotter, analyze_price_gaps

# Imports that are generic file/string/object/date utility functions
from libs.utils import name_parser, fund_list_extractor, index_extractor, index_appender, date_extractor
from libs.utils import configure_temp_dir, remove_temp_dir, create_sub_temp_dir
from libs.utils import download_data, has_critical_error, get_api_metadata
from libs.utils import TEXT_COLOR_MAP, SP500

# Imports that control function-only inputs
from libs.functions import only_functions_handler

# Imports that plot (many are imported in functions)
from libs.utils import candlestick

# Imports that drive custom metrics for market analysis
from libs.metrics import market_composite_index, bond_composite_index
from libs.metrics import correlation_composite_index, type_composite_index
from libs.metrics import future_returns, metadata_to_dataset

# Imports that create final products and show progress doing so
from libs.utils import ProgressBar, start_header
from libs.outputs import slide_creator, output_to_json

# Imports in development / non-final "public" calls
from test import test_competitive

####################################################################
####################################################################

PROCESS_STEPS = 13
################################
_VERSION_ = '0.1.23'
_DATE_REVISION_ = '2020-01-18'
################################


def technical_analysis(config: dict):

    config['process_steps'] = PROCESS_STEPS
    if config['release'] == True:
        # Use only after release!
        print(" ")
        print("~~~~ RELEASE 2 ~~~~ [deprecated but supported]")
        config = start_header(update_release=_DATE_REVISION_,
                              version=_VERSION_, options=True)
        config['process_steps'] = PROCESS_STEPS

    if config['state'] == 'halt':
        return

    if 'function' in config['state']:
        # If only simple functions are desired, they go into this handler
        only_functions_handler(config)
        return

    if 'no_index' not in config['state']:
        config['tickers'] = index_appender(config['tickers'])
        config['process_steps'] = config['process_steps'] + 2

     # Temporary directories to save graphs as images, etc.
    remove_temp_dir()
    configure_temp_dir()

    data, funds = download_data(config=config)

    e_check = {'tickers': config['tickers']}
    if has_critical_error(data, 'download_data', misc=e_check):
        return None

    # Start of automated process
    analysis = {}

    for fund_name in funds:

        fund = data[fund_name]
        fund_print = SP500.get(fund_name, fund_name)
        print("")
        print(f"~~{fund_print}~~")
        create_sub_temp_dir(fund_name)

        analysis[fund_name] = {}

        start = date_extractor(fund.index[0], _format='str')
        end = date_extractor(fund.index[len(fund['Close'])-1], _format='str')
        analysis[fund_name]['dates_covered'] = {
            'start': str(start), 'end': str(end)}
        analysis[fund_name]['name'] = fund_name

        p = ProgressBar(config['process_steps'], name=fund_print)
        p.start()

        analysis[fund_name]['statistics'] = get_high_level_stats(fund)

        analysis[fund_name]['metadata'] = get_api_metadata(
            fund_name, progress_bar=p, max_close=analysis[fund_name]['statistics']['max_close'])

        _, dat = cluster_oscs(fund, function='all', filter_thresh=3,
                              name=fund_name, plot_output=False, progress_bar=p)
        analysis[fund_name]['clustered_osc'] = dat

        analysis[fund_name]['rsi'] = RSI(
            fund, name=fund_name, plot_output=False, out_suppress=False, progress_bar=p)

        analysis[fund_name]['obv'] = on_balance_volume(
            fund, plot_output=False, name=fund_name, progress_bar=p)

        analysis[fund_name]['moving_average'] = triple_moving_average(
            fund, plot_output=False, name=fund_name, progress_bar=p)

        analysis[fund_name]['swing_trade'] = moving_average_swing_trade(
            fund, plot_output=False, name=fund_name, progress_bar=p)

        analysis[fund_name]['macd'] = mov_avg_convergence_divergence(
            fund, plot_output=False, name=fund_name, progress_bar=p)

        if 'no_index' not in config['state']:
            analysis[fund_name]['relative_strength'] = relative_strength(fund_name, full_data_dict=data, config=config,
                                                                         plot_output=False, meta=analysis[fund_name]['metadata'],
                                                                         progress_bar=p)
            beta, rsqd = beta_comparison(fund, data['^GSPC'])
            analysis[fund_name]['beta'] = beta
            analysis[fund_name]['r_squared'] = rsqd
            p.uptick()

        # Support and Resistance Analysis
        analysis[fund_name]['support_resistance'] = find_resistance_support_lines(
            fund, name=fund_name, plot_output=False, progress_bar=p)

        # Feature Detection Block
        analysis[fund_name]['features'] = {}
        analysis[fund_name]['features']['head_shoulders'] = feature_detection_head_and_shoulders(
            fund, name=fund_name, plot_output=False, progress_bar=p)

        filename = f"{fund_name}/candlestick_{fund_name}"
        candlestick(fund, title=fund_print, filename=filename,
                    saveFig=True, progress_bar=p)

        analysis[fund_name]['price_gaps'] = analyze_price_gaps(
            fund, name=fund_name, plot_output=False, progress_bar=p)

        # Get Trendlines
        analysis[fund_name]['trendlines'] = get_trendlines(
            fund, name=fund_name, plot_output=False, progress_bar=p)

        # Various Fund-specific Metrics
        analysis[fund_name]['futures'] = future_returns(
            fund, to_json=True, progress_bar=p)

        p.end()

    # test_competitive(data, analysis)

    analysis['_METRICS_'] = {}
    analysis['_METRICS_']['mci'] = market_composite_index(
        config=config, plot_output=False)

    bond_composite_index(config=config, plot_output=False)

    analysis['_METRICS_']['correlation'] = correlation_composite_index(
        config=config, plot_output=False)

    analysis['_METRICS_']['tci'] = type_composite_index(
        config=config, plot_output=False)

    slide_creator(analysis, config=config)
    output_to_json(analysis)

    metadata_to_dataset(config=config)

    remove_temp_dir()
