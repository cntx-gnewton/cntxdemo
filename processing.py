import pandas as pd
import io
import re
from os.path import join


def get_genome_data(genome_file):
    genome_data = pd.read_csv(
        genome_file,
        comment='#',
        sep='\t',
        header=None,
        names=['rsid', 'chromosome', 'position', 'genotype']
    )
    genome_data = genome_data.rename(columns={
        'chromosome': 'Chromosome',
        'position': 'Position',
        'genotype': 'Genotype'
    })
    return genome_data


def _risk_genotype_match(row):
    # Extract risk genotypes from the 'Risk Genotypes' column
    risk_genotypes = re.findall(
        r'\b\w+\b', str(row['Risk Genotypes']))
    user_genotype = row['Genotype']
    return user_genotype in risk_genotypes




def get_risk_genotypes(genome_data):
    # Read in snp_mapping
    snp_mapping = pd.read_csv(join('data', 'mapping.csv'))
    snp_mapping = snp_mapping.drop(columns=['Verified', 'Source'])
    # Merge user genome_data with snp_mapping
    merged_data = pd.merge(
        genome_data, snp_mapping, on='rsid', how='inner')
    # Match risk genotypes
    filtered_data = merged_data[merged_data.apply(
        _risk_genotype_match, axis=1)]
    return filtered_data
