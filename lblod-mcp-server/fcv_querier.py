"""
This module provides the FCVQUerier class to query
Flanders' Centrale Vindplaats SPARQL endpoint.

Author: @wdmuer
"""

from typing import Optional, List
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

    def getMunicipalOperatingAreaURI(self, municipalityName: str) -> str:
        """
        Retrieves the operating area's (werkingsgebied) URI of a municipality.

        Args:
            municipalityName (str): The name of the municipality.

        Returns:
            str: The URI of the municipal operating area if found, otherwise an empty string.
        """
        query = f"""
        SELECT * WHERE {{
	
        ?subject a <http://www.w3.org/ns/prov#Location> ;
          <http://mu.semte.ch/vocabularies/ext/werkingsgebiedNiveau> "Gemeente";
          <http://www.w3.org/2000/01/rdf-schema#label> ?object
        .FILTER regex(LCASE(STR(?object)), "{municipalityName.lower()}")
        }}
        """
        results = self.sparqlServer.query(query)
        try:
            bindings = results["results"]["bindings"]
            if bindings:
                return bindings[0]["subject"]["value"]
        except Exception as e:
            print(f"Error extracting municipal operating area URI: {e}")
        return ""

    def getGoverningUnitURIsForOperatingArea(self, operatingAreaURI: str) -> List[str]:
        """
        Retrieves the governing unit (bestuurseenheid) URIs for a given operating area URI.

        Args:
            operatingAreaURI (str): The URI of a municipal operating area.

        Returns:
            List[str]: A list of URIs of the governing units for the given municipal operating area if found, otherwise an empty list.
        """
        query = f"""
        SELECT * WHERE {{
	
        ?subject ?predicate <{operatingAreaURI}>
        }}
        """
        results = self.sparqlServer.query(query)
        try:
            bindings = results["results"]["bindings"]
            if bindings:
                return [body["subject"]["value"] for body in bindings]
        except Exception as e:
            print(f"Error extracting municipal operating area URI: {e}")
        return []

    def getGoverningBodyURIsForGoverningUnits(self, governingUnitURIs: List[str]) -> List[str]:
        """
        Retrieves the governing body (bestuursorgaan) URI for given governing unit URIs.

        Args:
            governingUnitURIs (List[str]): The list of URIs of municipal governing units.

        Returns:
            List[str]: List of URIs of the governing bodies for the given governing unit URIs.
                This list can be empty if no governing body can be found for any governing unit.
        """
        governingBodies = []

        for unitURI in governingUnitURIs:
            query = f"""
            SELECT * WHERE {{
        
            ?subject <http://data.vlaanderen.be/ns/besluit#bestuurt> <{unitURI}>
            }}
            """
            results = self.sparqlServer.query(query)
            try:
                bindings = results["results"]["bindings"]
                if bindings:
                    for unit in bindings:
                        governingBodies.append(unit["subject"]["value"])
            except Exception as e:
                print(f"Error extracting governing body URI: {e}")

        return governingBodies

    def getTimeSpecializationsForGoverningBodies(self, governingBodyURIs: List[str]) -> List[str]:
        """
        Retrieves the time specializations for given governing body URIs.

        Args:
            governingBodyURIs (List[str]): The list of URIs of municipal governing bodies.

        Returns:
            List[str]: List of URIs of the time specializations for the given governing bodies URIs.
                This list can be empty if no time specialization can be found for any governing body.
        """
        bodiesString = "\n  ".join(f"<{uri}>" for uri in governingBodyURIs)

        query = f"""
        PREFIX besluit: <http://data.vlaanderen.be/ns/besluit#>
        PREFIX eli: <https://data.vlaanderen.be/ns/generiek#>

        SELECT ?bestuursOrgaan WHERE {{
        VALUES ?orgaan {{
            {bodiesString}
        }}

        ?bestuursOrgaan a besluit:Bestuursorgaan ;
                eli:isTijdspecialisatieVan ?orgaan .
        }}
        """
        results = self.sparqlServer.query(query)
        try:
            print(results)
            bindings = results["results"]["bindings"]
            if bindings:
                return [body["bestuursOrgaan"]["value"] for body in bindings]
        except Exception as e:
            print(f"Error extracting municipal operating area URI: {e}")
        return []

    def getDecisionURIsFromTimeSpecializations(self, timeSpecializations: List[str], number: int = -1, order: str = "DESC") -> List[str]:
        """
        Gather decision URIs passed by the given time specializations, ordered from new to old or old to new,
        depending on the 'order' parameter.

        From the ordered results (if any), return the first 'number' decisions. If 'number' is -1, return all.

        Args:
            timeSpecializations (List[str]): URIs of time specializations of municipal governing bodies.
            number (int): Maximum number of decisions to return. Set to -1 to return all.
            order (str): Either "DESC" (newest first) or "ASC" (oldest first) to specify the sort order.

        Returns:
            List[str]: List of decision URIs.
                This list can be empty if no decisions were found that were passed by the given time specializations of governing bodies.
        """

        timeSpecializationsString = "\n  ".join(
            f"<{uri}>" for uri in timeSpecializations)

        query = f"""
        PREFIX besluit: <http://data.vlaanderen.be/ns/besluit#>
        PREFIX eli: <http://data.europa.eu/eli/ontology#>

        SELECT ?besluit WHERE {{
        VALUES ?orgaan {{
            {timeSpecializationsString}
        }}

        ?besluit a besluit:Besluit ;
                eli:passed_by ?orgaan ;
                eli:date_publication ?date .
        }}
        ORDER BY {order}(?date)
        """
        results = self.sparqlServer.query(query)
        try:
            bindings = results["results"]["bindings"]
            if bindings:
                decisions = [body["besluit"]["value"] for body in bindings]
                if number:
                    decisions = decisions[:number]
                return decisions
        except Exception as e:
            print(f"Error extracting municipal operating area URI: {e}")
        return []
