"""
This module provides a FastMCP tool for querying info from the LBLOD SPARQL endpoint.

The code is partly based on the mcp-server-sparql implementation by @ekzhu.
Link to his repo: https://github.com/ekzhu/mcp-server-sparql/tree/main.

Author: @wdmuer
"""

from typing import Dict, Any, Optional, Union
from SPARQLWrapper import SPARQLWrapper, JSON, SPARQLExceptions
from mcp.server.fastmcp import FastMCP


class SPARQLServer:
    """Wrapper for executing SPARQL queries on a given endpoint."""

    def __init__(self, endpointUrl: str):
        """
        Initializes the SPARQL server.

        Args:
            endpointUrl (str): The URL of the SPARQL endpoint.
        """
        self.endpointUrl = endpointUrl
        self.sparql = SPARQLWrapper(endpointUrl)
        self.sparql.setReturnFormat(JSON)

    def query(self, queryString: str) -> Dict[str, Any]:
        """
        Executes a SPARQL query.

        Args:
            queryString (str): The SPARQL query to execute.

        Returns:
            Dict[str, Any]: The query results in JSON format or an error message.
        """
        try:
            self.sparql.setQuery(queryString)
            results = self.sparql.query().convert()
            return results
        except SPARQLExceptions.EndPointNotFound:
            return {"error": f"SPARQL endpoint not found: {self.endpointUrl}"}
        except Exception as e:
            return {"error": f"Query error: {str(e)}"}


class MunicipalityQuerier:
    """Utility class for querying municipality information from Flanders' LBLOD SPARQL endpoint."""

    def __init__(self, sparqlServer: SPARQLServer):
        """
        Initializes the MunicipalityQuerier helper.

        Args:
            sparqlServer (SPARQLServer): An initialized SPARQLServer instance
                on the LBLOD SPARQL endpoint.
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


# Initialize the SPARQL server and helper
sparqlServer = SPARQLServer("https://data.lblod.info/sparql")
queryHelper = MunicipalityQuerier(sparqlServer)

# Start the FastMCP server
mcp = FastMCP("Municipality URI Query Tool")


@mcp.tool(description="""
Get the URI of a municipality based on a partial or full name.

Args:
    name: The (partial) name of the municipality (e.g., 'Gent', 'Aalst').

Returns:
    A string with the URI of the matched municipality, or an error message.
""")
def getMunicipalityUri(name: str) -> Union[str, Dict[str, str]]:
    """
    FastMCP tool: Get municipality URI from name.

    Args:
        name (str): Municipality name or partial name.

    Returns:
        Union[str, Dict[str, str]]: Municipality URI or error.
    """
    uri = queryHelper.getMunicipalityUri(name)
    if not uri:
        return {"error": f"No municipality URI found for name: {name}"}
    return uri


if __name__ == "__main__":
    mcp.run(transport="stdio")
