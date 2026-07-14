import { useQuery } from "@tanstack/react-query";
import { api } from "@/shared/api/client";
import type { Service } from "./types";

async function fetchServices(): Promise<Service[]> {
  const { data } = await api.get<Service[]>("/services");
  return data;
}

export function useServices() {
  return useQuery({ queryKey: ["services"], queryFn: fetchServices });
}
