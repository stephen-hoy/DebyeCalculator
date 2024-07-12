#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Rough script to replace the neutron cross-section data from the 
   original elements_info.yaml with neutron scattering length data, 
   retaining original YAML formatting.
   (Data source: https://www.ncnr.nist.gov/resources/n-lengths/list.html)
"""
__author__ = "Stephen A. Hoy"
__date__ = "2024-07-11"

from ruamel.yaml import YAML
import pandas as pd
import os

yaml = YAML()
yaml.width = 4096
yaml.top_level_colon_align = 5

yaml.Emitter.flow_seq_start = " [  "
yaml.Emitter.flow_seq_separator = ",  "

with open("dbc_modded/utility/elements_info.yaml", "r") as elements_file:
    elements_table = yaml.load(elements_file)

nist_table = pd.read_csv("nist_scattering_data.csv", index_col="Isotope")

for element in list(nist_table.index.values):
    if element in elements_table and elements_table[element][11] is not None:
        if nist_table.loc[element]["Coh b"] == "---":
            elements_table[element][11] = 0.0
        else:
            b_without_uncertainty = nist_table.loc[element]["Coh b"].split("(")[0]
            b_real = complex(b_without_uncertainty.replace("i", "j")).real
            elements_table[element][11] = b_real

with open("dbc_modded/utility/tmp_elements_info.yaml", "w") as output_file:
    yaml.dump(elements_table, output_file)

with open("dbc_modded/utility/tmp_elements_info.yaml", "r") as pretty_output:
    raw_output = pretty_output.readlines()

new_lines = []
for line in raw_output[21:231]:
    line_by_commas = line.split(",")
    prefix = line_by_commas[0].split("[")[1]
    if len(prefix) < 10:
        prefix = (" " * (10 - len(prefix))) + prefix

    if len(prefix) > 10:
        prefix = prefix[(len(prefix) - 10) :]

    new_prefix = line_by_commas[0].split("[")[0] + "[" + prefix

    body = line_by_commas[1:12]
    new_body = []
    for col in body:
        if len(col) < 11:
            new_body.append(" " * (11 - len(col)) + col)
        elif len(col) > 11:
            new_body.append(col[(len(col) - 11) :])
        else:
            new_body.append(col)

    suffix = line_by_commas[12:]
    new_suffix = []

    if len(suffix[0]) < 13:
        new_suffix.append(" " * (13 - len(suffix[0])) + suffix[0])
    elif len(suffix[0]) > 13:
        new_suffix.append(suffix[0][(len(suffix[0]) - 13) :])
    else:
        new_suffix.append(suffix[0])

    if len(suffix[1]) < 15:
        new_suffix.append(" " * (15 - len(suffix[1])) + suffix[1])
    elif len(suffix[1]) > 15:
        new_suffix.append(suffix[1][(len(suffix[1]) - 15) :])
    else:
        new_suffix.append(suffix[1])

    new_lines.append(new_prefix + "," + ",".join(new_body) + "," + ",".join(new_suffix))

with open("dbc_modded/utility/new_elements_info.yaml", "w") as pretty_output:
    pretty_output.writelines(raw_output[:21])
    pretty_output.writelines(new_lines)
    pretty_output.writelines(raw_output[231])

os.rename(
    "dbc_modded/utility/elements_info.yaml", "dbc_modded/utility/old_elements_info.yaml"
)

os.rename(
    "dbc_modded/utility/new_elements_info.yaml", "dbc_modded/utility/elements_info.yaml"
)

if os.path.exists("dbc_modded/utility/tmp_elements_info.yaml"):
    os.remove("dbc_modded/utility/tmp_elements_info.yaml")
