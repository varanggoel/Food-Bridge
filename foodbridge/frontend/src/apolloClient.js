import { ApolloClient, InMemoryCache, HttpLink } from "@apollo/client";

const GRAPHQL_URL = import.meta.env.VITE_GRAPHQL_URL || "http://127.0.0.1:8000/graphql";

export const client = new ApolloClient({
  link: new HttpLink({ uri: GRAPHQL_URL, fetchOptions: { mode: "cors" } }),
  cache: new InMemoryCache(),
});
