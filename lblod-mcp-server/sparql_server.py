"""
This module provides the SPARQLServer class to connect with and query a SPARQL endpoint.

The code is based on the mcp-server-sparql implementation by @ekzhu.
Link to his repo: https://github.com/ekzhu/mcp-server-sparql/tree/main.

Author: @wdmuer
"""

from typing import Dict, Any
from SPARQLWrapper import SPARQLWrapper, JSON, SPARQLExceptions, POST


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
            self.sparql.setMethod(POST)
            results = self.sparql.query().convert()
            return results
        except SPARQLExceptions.EndPointNotFound:
            return {"error": f"SPARQL endpoint not found: {self.endpointUrl}"}
        except Exception as e:
            return {"error": f"Query error: {str(e)}"}
