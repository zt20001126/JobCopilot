export interface JobInfo {
  platform: "boss";
  positionTitle: string;
  jobDescription: string;
  jobUrl: string;
}

export interface JobPageDiagnostic {
  pageUrl: string;
  urlSupported: boolean;
  titleFound: boolean;
  descriptionFound: boolean;
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
  request_id?: string;
  generated_at?: string;
  model_name?: string;
}

export type ExtensionMessage =
  | { type: "GET_JOB_INFO" }
  | { type: "GET_PAGE_DIAGNOSTIC" }
  | { type: "JOB_INFO_UPDATED"; payload: JobInfo | null }
  | { type: "OPEN_SIDE_PANEL" }
  | { type: "GENERATE_GREETING"; payload: GreetingRequest };

export interface ExtensionMessageResponse<T> {
  ok: boolean;
  data?: T;
  error?: string;
}
