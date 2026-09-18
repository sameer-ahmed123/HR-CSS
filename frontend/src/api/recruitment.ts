import client from "./client";
import type {
  HiringRequest,
  HiringRequestInput,
  RecruitmentOverview,
  JobPosting,
  JobPostingInput,
  JobStatus,
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
  updateHiringRequestStatus: (
    id: number,
    status: "APPROVED" | "REJECTED" | "MORE_INFO",
    rejection_reason?: string,
    createJobPosting = false,
  ) =>
    client.patch<HiringRequest>(`/recruitment/hiringreq/${id}/status/`, {
      status,
      rejection_reason,
      create_job_posting: createJobPosting,
    }),
  listJobPostings: (params?: { status?: JobStatus; department?: number }) =>
    client.get<JobPosting[]>("/recruitment/job-postings/", { params }),
  createJobPosting: (data: JobPostingInput) =>
    client.post<JobPosting>("/recruitment/job-postings/", data),
  getJobPosting: (id: number) =>
    client.get<JobPosting>(`/recruitment/job-postings/${id}/`),
  updateJobPosting: (id: number, data: Partial<JobPostingInput>) =>
    client.patch<JobPosting>(`/recruitment/job-postings/${id}/`, data),
  deleteJobPosting: (id: number) =>
    client.delete(`/recruitment/job-postings/${id}/`),
  changeJobPostingStatus: (id: number, status: JobStatus) =>
    client.patch<JobPosting>(`/recruitment/job-postings/${id}/status/`, { status }),
};