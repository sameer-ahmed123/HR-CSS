import { useState, type InputHTMLAttributes } from "react";
import axios from "axios";
import { UserPlus, X } from "lucide-react";
import { useForm } from "react-hook-form";
import { authApi } from "../../api/auth";
import { organizationApi } from "../../api/organization";
import type { Department, InviteCredentials, UserRole } from "../../types";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { Label } from "../ui/label";
import { Alert, type AlertTone } from "../ui/alert";

const roles: UserRole[] = ["EMPLOYEE", "TEAM_LEAD", "FINANCE", "HR"];

export default function InviteMemberDialog() {
  const [open, setOpen] = useState(false);
  const [feedback, setFeedback] = useState("");
  const [feedbackTone, setFeedbackTone] = useState<AlertTone>("info");
  const [departments, setDepartments] = useState<Department[]>([]);
  const [departmentsLoading, setDepartmentsLoading] = useState(false);
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<InviteCredentials>({ defaultValues: { role: "EMPLOYEE" } });

  async function openDialog() {
    setOpen(true);
    setFeedback("");
    setDepartmentsLoading(true);
    try {
      const { data } = await organizationApi.listDepartments();
      setDepartments(data);
    } catch {
      setFeedbackTone("error");
      setFeedback("We could not load departments. Please try again.");
    } finally {
      setDepartmentsLoading(false);
    }
  }

  async function submit(values: InviteCredentials) {
    setFeedback("");
    try {
      await authApi.createInvite({
        ...values,
        department: values.department,
      });
      reset({ role: "EMPLOYEE" });
      setFeedbackTone("success");
      setFeedback("Invitation sent successfully.");
    } catch (error) {
      setFeedbackTone("error");
      setFeedback(getInviteErrorMessage(error));
    }
  }

  return (
    <>
      <Button type="button" onClick={openDialog}>
        <UserPlus size={17} /> Invite member
      </Button>
      {open && (
        <div
          className="fixed inset-0 z-50 grid place-items-center bg-ink/40 px-4"
          role="dialog"
          aria-modal="true"
          aria-labelledby="invite-member-title"
        >
          <div className="w-full max-w-lg rounded-3xl bg-white p-6 shadow-xl">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-xs font-bold uppercase tracking-[0.16em] text-coral">
                  People
                </p>
                <h2
                  id="invite-member-title"
                  className="mt-2 font-display text-2xl font-bold"
                >
                  Invite a new member
                </h2>
              </div>
              <button
                type="button"
                onClick={() => setOpen(false)}
                aria-label="Close invite dialog"
                className="rounded-lg p-2 hover:bg-surface"
              >
                <X size={18} />
              </button>
            </div>
            <form onSubmit={handleSubmit(submit)} className="mt-6 space-y-4">
              <div className="grid gap-4 sm:grid-cols-2">
                <Field
                  label="First name"
                  error={errors.first_name?.message}
                  {...register("first_name", { required: "Required" })}
                />
                <Field
                  label="Last name"
                  error={errors.last_name?.message}
                  {...register("last_name", { required: "Required" })}
                />
              </div>
              <Field
                label="Work email"
                type="email"
                error={errors.email?.message}
                {...register("email", { required: "Required" })}
              />
              <div className="grid gap-4 sm:grid-cols-2">
                <Label className="block">
                  Role
                  <select
                    className="mt-2 h-10 w-full rounded-lg border border-ink/15 bg-white px-3 text-sm"
                    {...register("role")}
                  >
                    {roles.map((role) => (
                      <option key={role} value={role}>
                        {role.replace("_", " ")}
                      </option>
                    ))}
                  </select>
                </Label>
                <Label className="block">
                  Department
                  <select
                    className="mt-2 h-10 w-full rounded-lg border border-ink/15 bg-white px-3 text-sm"
                    disabled={departmentsLoading}
                    {...register("department", {
                      required: "Select a department",
                      valueAsNumber: true,
                      validate: (value) => value > 0 || "Select a department",
                    })}
                  >
                    <option value="">
                      {departmentsLoading
                        ? "Loading departments..."
                        : "Select a department"}
                    </option>
                    {departments.map((department) => (
                      <option key={department.id} value={department.id}>
                        {department.name} ({department.code})
                      </option>
                    ))}
                  </select>
                  {errors.department && (
                    <span className="mt-1 block text-xs font-normal text-red-700">
                      {errors.department.message}
                    </span>
                  )}
                </Label>
              </div>
              {feedback && <Alert tone={feedbackTone}>{feedback}</Alert>}
              <Button type="submit" disabled={isSubmitting} className="w-full">
                {isSubmitting ? "Sending invitation..." : "Send invitation"}
              </Button>
            </form>
          </div>
        </div>
      )}
    </>
  );
}

function getInviteErrorMessage(error: unknown) {
  if (!axios.isAxiosError(error)) {
    return "We could not send this invitation. Check the details and try again.";
  }
  const data = error.response?.data as Record<string, unknown> | undefined;
  if (typeof data?.detail === "string") return data.detail;
  for (const value of Object.values(data ?? {})) {
    if (Array.isArray(value) && typeof value[0] === "string") return value[0];
    if (typeof value === "string") return value;
  }
  return "We could not send this invitation. Check the details and try again.";
}

const Field = ({
  label,
  error,
  ...props
}: {
  label: string;
  error?: string;
} & InputHTMLAttributes<HTMLInputElement>) => (
  <Label className="block">
    {label}
    <Input className="mt-2 border border-ink/15 px-3" {...props} />
    {error && (
      <span className="mt-1 block text-xs font-normal text-red-700">
        {error}
      </span>
    )}
  </Label>
);
