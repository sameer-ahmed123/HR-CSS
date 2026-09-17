import client from "./client";
import type {
  HiringRequest,
  HiringRequestInput,
  RecruitmentOverview,
} from "../types";

export const recruitmentApi = {
  getOverview: () => client.get<RecruitmentOverview>("/recruitment/overview/"),
  listHiringRequests: () => client.get<HiringRequest[]>("/recruitment/hiringreq/"),
  createHiringRequest: (data: HiringRequestInput) =>
    client.post<HiringRequest>("/recruitment/hiringreq/", data),
  getHiringRequest: (id: number) =>
    client.get<HiringRequest>(`/recruitment/hiringreq/${id}/`),
  updateHiringRequest: (id: number, data: Partial<HiringRequestInput>) =>
    client.patch<HiringRequest>(`/recruitment/hiringreq/${id}/`, data),
  deleteHiringRequest: (id: number) =>
    client.delete(`/recruitment/hiringreq/${id}/`),
};