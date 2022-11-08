import numpy as np 
import pandas as pd 
from typing import Union, Tuple 
from pysage.units.units_table_db import  units_table, symbols_for_measurement, symbols_for_system,dimensionless_symbols

def is_known_unit(symbol:str):

    """
    Returns true if the unit symbol is known and returns false otherwise

        Example:
        
        unit_convert.is_known_unit('degC')        #returns True 

        unit_convert.is_known_unit('xxxxdegC')    #returns False
        
    """
    return symbol in units_table 
    
   
def convert_to_system( system_name:str, measurement:Union[np.ndarray,int,float], symbol:str )->Tuple[ Union[np.ndarray,int,float],str]:
    
    if isinstance(measurement, np.ndarray) or isinstance(measurement, float ) or isinstance(measurement, int ) :
        offset = units_table[symbol][system_name]['offset']
        return measurement*units_table[symbol][system_name]['scale'] + offset, units_table[symbol][system_name]['symbol']
    
    if isinstance( measurement, list):
        all_numbers = all([isinstance(item, int) or isinstance(item, float) for item in measurement])
        if  all_numbers:
            offset = units_table[symbol][system_name]['offset']
            return np.array([item * units_table[symbol][system_name]['scale'] + offset for item in measurement]) , units_table[symbol][system_name]['symbol']
        else:
            raise ValueError('Cannot convert non-numeric values. Please use a list of numbers')

    raise ValueError('Cannot convert',type(measurement), ' please use a list, number or np array')
  
  
def convert_to_canonical( measurement:Union[np.ndarray,int,float], symbol:str )->Tuple[ Union[np.ndarray,int,float],str]:
    return convert_to_system('canonical',measurement,symbol)


def convert_to_metric( measurement:Union[np.ndarray,int,float], symbol:str )->Tuple[ Union[np.ndarray,int,float],str]:
    """
    Converts multiple values of a quntity in a list or a numpy array, or converts a single value given as an integer or a float, to 
    the values in the Metric system. The initial values are assumed to be in units given by the symbol passed as the second argument. 
    For example: m (meter) or GPa (Giga pascal).
    
        Parameters:
    
        measurement: A numpy array, a list, or a single integer or float representing a measurement.
        symbol: The units symbol of the measurement, e.g. KPa (for kilo Pascal)
    
        Returns:
        1. A numpy array, list or single value with the measurement expressed in the English units system. 
        2. The symbol of the measurement in the english system
        
 
        Example: 
        
        values, new_symbol = unit_convert.convert_to_english( [1,2,3], 'm')
        print(values, new_symbol )
        
        result: 
        98.0665 kPa  
    """
    return convert_to_system('metric',measurement,symbol)
   
   
def convert_to_english( measurement:Union[np.ndarray,list,int,float], symbol:str )->Tuple[ Union[np.ndarray,int,float],str]:
    """
    Converts multiple values of a quntity in a list or a numpy array, or converts a single value given as an integer or a float, to 
    the values in the English system. The initial values are assumed to be in units given by the symbol passed as argument. 
    For example: m (meter) or GPA (Giga pascal).
    
        Parameters:
    
        measurement: A numpy array, a list, or a single integer or float representing a measurement.
        symbol: The units symbol of the measurement, e.g. KPa (for kilo Pascal)
    
        Returns:
        1. A numpy array, list or single value with the measurement expressed in the English units system. 
        2. The symbol of the measurement in the english system
        
 
        Example: 
        
        values, symbol = unit_convert.convert_to_english( [1,2,3], 'm')
        print(values, symbol )
        
        result: 
        [3.2808399  6.56167979 9.84251969] ft
    """
    return convert_to_system('english',measurement,symbol)


def convert( measurement:Union[np.ndarray,int,float], symbol1:str , symbol2:str ):
    
    if units_table[symbol1]['measurement'] == units_table[symbol2]['measurement']:
        
        f1,_ = convert_to_canonical(measurement,symbol1)
        offset = units_table[symbol2]['canonical']['offset']
        return  (f1-offset)/units_table[symbol2][ 'canonical'] ['scale']
        
    print('Cannot convert from ', symbol1,'to',symbol2,'. Not the same base measurement ', units_table[symbol1]['measurement'],'->', units_table[symbol2]['measurement'])
    raise ValueError('Cannot convert from ' + symbol1 + ' to ' +symbol2+' because they arent of the same base measurement')
   
   
def print_conversions( value, init_symbol ):   

    print( units_table[init_symbol]['name'],"(", units_table[init_symbol]['measurement'],")" )
    for system in ['canonical','metric','english']:
        converted, symbol = convert_to_system( system, value, init_symbol)
        if symbol!=init_symbol: 
            name2 = units_table[init_symbol][system][ 'name']
            print('{} {} converted to {} in the {} system equals {} {}'.format(value,init_symbol,symbol, system, converted, name2 ))


def convert_dataframe_to_canonical( df:pd.DataFrame, units:dict )->pd.DataFrame:

    numeric_columns = df.select_dtypes(include=[np.number]).columns

    for log_name in numeric_columns:
        
        log_units  = units.get(log_name, '_')
        
        if log_units in units_table:
          
            log_values = df[log_name].to_numpy()
            new_log, new_symbol = convert_to_canonical( log_values, log_units) 
            new_log, new_symbol

            #update the data 
            df[log_name] = new_log
            units[log_name] = new_symbol
        else:
            print( '{} was not converted because the unit {} is not known '.format(log_name,log_units))
    