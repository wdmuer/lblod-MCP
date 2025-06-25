"""
This module provides a FastMCP tool for querying info from
Flanders' Centrale Vindplaats SPARQL endpoint.

The code is based on the mcp-server-sparql implementation by @ekzhu.
Link to his repo: https://github.com/ekzhu/mcp-server-sparql/tree/main.

Author: @wdmuer
"""

from typing import Dict, Union, List
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


@mcp.tool(description="""
Get 'number' newest/oldest decision URIs made in a municipality based on its name.

Args:
    name: The name of the municipality (e.g., 'Gent', 'Aalst', 'Lanaken').
    number (int): Maximum number of decisions to return. Set to -1 to return all.
    order (str): Either "DESC" (newest first) or "ASC" (oldest first) to specify the sort order.

Returns:
    A list of decision URIs.
          
Note:
    This tool returns only actual URIs retrieved from a trusted data source.
    If no decisions are found, the returned list will be empty.
    The tool does not infer, summarize, or describe the content of any decisions.
""")
def getDecisionURIs(name: str, number: int, order: str) -> List[str]:
    """
    FastMCP tool: Get decision URIs from a municipality.

    Args:
        name (str): Municipality name.
        number (int): Maximum number of decisions to return. Set to -1 to return all.
        order (str): Either "DESC" (newest first) or "ASC" (oldest first) to specify the sort order.

    Returns:
        List[str]: List of decision URIs, can be empty in case no decisions were found.
    """
    operatingAreaURI = queryHelper.getMunicipalOperatingAreaURI(name)

    governingUnits = queryHelper.getGoverningUnitURIsForOperatingArea(
        operatingAreaURI)

    governingBodies = queryHelper.getGoverningBodyURIsForGoverningUnits(
        governingUnits)

    timeSpecializations = queryHelper.getTimeSpecializationsForGoverningBodies(
        governingBodies)

    decisions = queryHelper.getDecisionURIsFromTimeSpecializations(
        timeSpecializations, number, order)

    if decisions == []:
        decisions = [
            f"No URIs found! Reply with this exact message: No decision URIs for {name} could be found"]

    return decisions


if __name__ == "__main__":
    mcp.run(transport="stdio")
