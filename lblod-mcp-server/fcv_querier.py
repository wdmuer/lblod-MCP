"""
This module provides the FCVQUerier class to query
Flanders' Centrale Vindplaats SPARQL endpoint.

Author: @wdmuer
"""

from typing import Optional
from sparql_server import SPARQLServer


class FCVQuerier:
    """Utility class for querying municipality information from Flanders' Centrale Vindplaats SPARQL endpoint."""

    def __init__(self, sparqlServer: SPARQLServer):
        """
        Initializes the class FCVQuerier helper.

        Args:
            sparqlServer (SPARQLServer): An initialized SPARQLServer instance
                on Flanders' Centrale Vindplaats SPARQL endpoint.
        """
        self.sparqlServer = sparqlServer

    def getMunicipalityUri(self, name: str) -> Optional[str]:
        """
        Retrieves the URI of a municipality by name,
        restricted to entities classified as 'gemeente'.

        Args:
            name (str): The name (or partial name) of the municipality.

        Returns:
            Optional[str]: The URI of the municipality if found, otherwise None.
        """
        query = f"""
        PREFIX besluit: <http://data.vlaanderen.be/ns/besluit#>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

        SELECT DISTINCT ?municipality ?label
        WHERE {{
            ?municipality a besluit:Bestuurseenheid ;
                besluit:classificatie <http://data.vlaanderen.be/id/concept/BestuurseenheidClassificatieCode/5ab0e9b8a3b2ca7c5e000001> ;
                skos:prefLabel ?label .
            FILTER(CONTAINS(LCASE(STR(?label)), "{name.lower()}"))
        }}
        LIMIT 1
        """
        results = self.sparqlServer.query(query)
        try:
            bindings = results["results"]["bindings"]
            if bindings:
                return bindings[0]["municipality"]["value"]
        except Exception as e:
            print(f"Error extracting municipality URI: {e}")
        return None

    def getMunicipalCouncilUri(self, municipalityUri: str) -> Optional[str]:
        """
        Retrieves the URI of a municipal council via the municipality URI,
        restricted to entities classified as 'Gemeenteraad'.

        Args:
            name (str): The URI of the municipality.

        Returns:
            Optional[str]: The URI of the municipal council if found, otherwise None.
        """
        query = f"""
        PREFIX besluit: <http://data.vlaanderen.be/ns/besluit#>

        SELECT DISTINCT ?gemeenteraad
        WHERE {{
        BIND (<{municipalityUri}> AS ?gemeente)

        ?gemeenteraad a besluit:Bestuursorgaan ;
                        besluit:bestuurt ?gemeente ;
                        besluit:classificatie <http://data.vlaanderen.be/id/concept/BestuursorgaanClassificatieCode/5ab0e9b8a3b2ca7c5e000005> .
        }}
        LIMIT 1
        """
        results = self.sparqlServer.query(query)
        try:
            bindings = results["results"]["bindings"]
            if bindings:
                return bindings[0]["gemeenteraad"]["value"]
        except Exception as e:
            print(f"Error extracting municipality URI: {e}")
        return None
