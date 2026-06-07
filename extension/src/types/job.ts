export interface JobInfo {
  platform: "boss";
  positionTitle: string;
  jobDescription: string;
  jobUrl: string;
}

export interface GreetingRequest {
  position_title: string;
  job_description: string;
  job_url?: string;
}

export interface GreetingResponse {
  simple_version: string;
  professional_version: string;
  high_reply_version: string;
}

export type ExtensionMessage =
  | { type: "GET_JOB_INFO" }
  | { type: "GENERATE_GREETING"; payload: GreetingRequest };

export interface ExtensionMessageResponse<T> {
  ok: boolean;
  data?: T;
  error?: string;
}
