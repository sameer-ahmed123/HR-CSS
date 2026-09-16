import client from "./client";
import type { Department } from "../types";

export const organizationApi = {
  listDepartments: () => client.get<Department[]>("/organization/departments/"),
};