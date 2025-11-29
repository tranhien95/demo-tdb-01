from indicators import indicator_manager

indicators = indicator_manager.list_indicators()
print(f'Total: {len(indicators)} indicators')
print('\nAll indicators:')
for i, ind in enumerate(indicators, 1):
    config = indicator_manager.get_indicator_config(ind)
    desc = config.get('description', 'N/A')
    print(f'{i:2}. {ind:25} - {desc}')
