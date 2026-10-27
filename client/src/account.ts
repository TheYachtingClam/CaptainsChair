import { useQuery } from "@tanstack/react-query";
import { api } from "./api";

/** The signed-in account, or undefined while it loads. */
export function useAccount() {
  const me = useQuery({ queryKey: ["me"], queryFn: api.me, retry: false, staleTime: 60_000 });
  return me.data;
}
