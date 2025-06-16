"""
This module provides a FastMCP tool for querying info from
Flanders' Centrale Vindplaats SPARQL endpoint.

The code is based on the mcp-server-sparql implementation by @ekzhu.
Link to his repo: https://github.com/ekzhu/mcp-server-sparql/tree/main.

Author: @wdmuer
"""

from typing import Dict, Union
from mcp.server.fastmcp import FastMCP
from sparql_server import SPARQLServer
from fcv_querier import FCVQuerier

# Initialize the SPARQL server and helper
sparqlServer = SPARQLServer("https://data.lblod.info/sparql")
queryHelper = FCVQuerier(sparqlServer)

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
