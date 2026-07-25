import { ApolloClient, InMemoryCache, HttpLink } from "@apollo/client";

const getGraphqlUrl = () => {
  const configured = import.meta.env.VITE_GRAPHQL_URL?.trim();
  if (configured) return configured;

  if (typeof window !== "undefined") {
    const { protocol, hostname } = window.location;
    if (hostname === "localhost" || hostname === "127.0.0.1") {
      return "http://127.0.0.1:8000/graphql";
    }
  }

  return "/graphql";
};

export const client = new ApolloClient({
  link: new HttpLink({ uri: getGraphqlUrl(), fetchOptions: { mode: "cors" } }),
  cache: new InMemoryCache(),
});
