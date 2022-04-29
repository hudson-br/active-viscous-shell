#!/usr/bin/env python3
# gen_config.py

import numpy as np
import configreader as cr
import os
import sys

def set_value(configuration, param_name, param_value)  :
    """
    set_value(configuration, param_name, param_value)
    
        Set the value of param_name to param_value in the configuration
        
        Parameters
        ----------
        configuration : config
            The input configuration
        param_name : str
            The name of the parameter to change
        param_value : str, float, int
            New value of the parameter
            
        Returns
        -------
        configuration : config
            The new modified configuration
            
        Example
        -------
        set_value(config, param_name='radius', param_value=1.)
        
        Changes the parameter "radius" to 1.
    """
    for cat in configuration.keys() :
        for name in configuration[cat].keys() :
            if name == param_name :
                configuration[cat][name] = param_value
                
    return configuration
                
    
def make_outdir(loc='', tpl='run', pad=0) :
    """
    make_outdir(loc='', tpl='run', pad=0)
    
        Create a folder starting starting with tpl followed by padding, at location loc.
        If the folder already exists, delete the files contained in
        
        Parameters
        ----------
        loc : str, optional, default : ''
            Location of the output folder.
            
        tpl : str, optional, default : 'run'
            Prefix of the directory
            
        pad : int, optional, default : 0
            Default padding, to have run0000, run0001, run0002, etc.
            
        Returns
        -------
        outdir_name : str
            Name of the created folder.
    """
    outdir_name = os.path.join(loc, tpl+str(pad).zfill(4))
    try :
        os.mkdir(outdir_name)
    except :
        # Clean up the directory
        for elem in os.listdir(outdir_name) :
            os.remove(os.path.join(outdir_name, elem))
        
    return outdir_name
                 
def generate_configuration_files(tpl_name, param_name, param_value, loc='', dirname='run', out_configname='config.conf') :
    """
    generate_configuration_files(tpl_name, param_name, param_value, loc='', dirname='run', out_configname='config.conf')
    
        Generate folder(s) containing a configuration file modified from a template configuration file.
        
        Parameters
        ----------
        tpl_name : str
            Name of the configuration template
            
        param_name : str
            Name of the parameter to modify. This is a unique key in the configuration.
        
        param_value : str, float or range
            Value or range of value to attribute to the parameter. Can be a list or an array.
        
        loc : str, optional, default : ''
            Location of the output folders.
        
        dirname : str, optional, default : 'run'
            Prefix of the directories.
        
        out_configname : str, optional, default : 'config.conf'
            Name of the output configuration files once generated.
            
        Returns
        -------
        0 : if one file was generated
        1 : if several files were generated

        Example
        -------
        generate_configuration_files(tpl_name='config.conf.tpl', param_name='radius', param_value=np.linspace(0., 1., 10))
    """
    # Generate a configuration object
    C = cr.Config()
    # Read the template configuration file
    config = C.read(tpl_name)
    
    
    # Case 1 : if a range of values is specified
    if len(np.shape(param_value)) > 0 :
        
        nsim = np.shape(param_value)[0]
        
        for i in range(nsim) :
            # Create a new configuration dictionnary containing the change
            new_config = set_value(config, param_name, param_value[i])
            # Create the output directory
            outdir = make_outdir(loc, tpl=dirname, pad=i)
            # Write the new configuration in the output directory
            C.write(os.path.join(outdir, out_configname))
            
        return 1;
        
    # Case 2 :  if a single scalar is specified
    else :
        # Create a new configuration dictionnary containing the change
        new_config = set_value(config, param_name, param_value)
        # Create the output directory
        outdir = make_outdir(loc, tpl=dirname)
        # Write the new configuration at loc
        C.write(os.path.join(outdir, out_configname))
        
        return 0;
    
def read_pvalue(pvalue) :
    """
    read_pvalue(pvalue)
    """
    if pvalue.startswith('[') and pvalue.endswith(']') :
        pval = [float(elem) for elem in pvalue[1:-1].split(',')]
        
    elif pvalue.startswith('np') or pvalue.startswith('numpy') :
        if pvalue.startswith('np') : prefix = 'np'
        else : prefix = 'numpy'
        pval = interpret_np(pvalue)
        
    else :
        try :
            pval = eval(pvalue)
        except :
            pval = pvalue
            pass
        
    return pval

def interpret_np(instruction, prefix='np') :
    """
    interpret_np(instruction, prefix='np')
    """
    if instruction[len(prefix):].startswith('.linspace') :
        s = instruction[len(prefix)+len('.linspace')+1 : -1].split(',')
        pmin = float(s[0])
        pmax = float(s[1])
        dp = int(s[2])
        p = np.linspace(pmin, pmax, dp)
        
    elif instruction[len(prefix):].startswith('.arange') :
        s = instruction[len(prefix)+len('.arange')+1 : -1].split(',')
        pmin = float(s[0])
        pmax = float(s[1])
        dp = int(s[2])
        p = np.arange(pmin, pmax, dp)
        
    else : return None
    
    return p
    
def main(tpl, args) :
    # Default Arguments
    loc = ''
    dirname = 'run'
    out_configname = 'config.conf'
    
    if len(args) > 0 :
        for arg in args :
            if arg.startswith('tpl=') :
                tpl = arg[len('tpl='):]
            elif arg.startswith('pname=') :
                pname = arg[len('pname='):]
            elif arg.startswith('pvalue=') :
                pvalue = arg[len('pvalue='):]
                pvalue = read_pvalue(pvalue)
            elif arg.startswith('loc=') :
                loc = arg[len('loc='):]
            elif arg.startswith('dirname=') :
                dirname = arg[len('dirname='):]
            elif arg.startswith('out_configname=') :
                out_configname = arg[len('out_configname='):]
        
    generate_configuration_files(tpl, pname, pvalue, loc, dirname=dirname, out_configname=out_configname)
                
    
if __name__ == '__main__' :
    if len(sys.argv) < 2:
        print('[network_simulation.py] Error: missing config file, type help for instructions.')
    elif sys.argv[1]=='help' or sys.argv[1]=='-h':
        print(__doc__)
    # first argument should be a readable config file:
    elif os.access(sys.argv[1], os.R_OK):
        conf_name = sys.argv[1]
        args = []
        try :
            args = sys.argv[1:]
        except :
            pass
            
        main(conf_name, args)
    else :
        print('Error : no readable config file found')
        print(sys.argv[1])
    sys.exit()