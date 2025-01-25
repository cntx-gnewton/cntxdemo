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
    snp_mapping = pd.read_csv(join('data', 'new_mapping.csv'))
    snp_mapping = snp_mapping.drop(columns=['Source'])
    # Merge user genome_data with snp_mapping
    merged_data = pd.merge(
        genome_data, snp_mapping, on='rsid', how='inner')
    # Match risk genotypes
    filtered_data = merged_data[merged_data.apply(
        _risk_genotype_match, axis=1)]
    return filtered_data


def get_environmental_risks(user_risk_df, user_environmental_factors):
    """Match user's risk SNPs with environmental factors."""
    environmental_mapping = pd.read_csv('environmental_mapping.csv')
    # Merge user risk SNPs with environmental mapping
    merged_env_data = pd.merge(user_risk_df, environmental_mapping, on=[
                               'rsid', 'Gene'], how='inner')
    # Filter based on user environmental factors

    def is_environmental_risk(row):
        env_factors = [e.strip().lower()
                       for e in row['Environmental Factor'].split(';')]
        user_env_factors_lower = [e.lower()
                                  for e in user_environmental_factors]
        return any(env in user_env_factors_lower for env in env_factors)
    user_env_risk_df = merged_env_data[merged_env_data.apply(
        is_environmental_risk, axis=1)]
    return user_env_risk_df
