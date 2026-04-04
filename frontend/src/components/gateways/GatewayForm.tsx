import type { FormEvent } from "react";

import type { GatewayCheckStatus } from "@/lib/gateway-form";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export const GATEWAY_TYPE_OPENCLAW = "openclaw";
export const GATEWAY_TYPE_UIPATH = "uipath";

type GatewayFormProps = {
  name: string;
  gatewayType: string;
  gatewayUrl: string;
  gatewayToken: string;
  disableDevicePairing: boolean;
  workspaceRoot: string;
  allowInsecureTls: boolean;
  gatewayUrlError: string | null;
  gatewayCheckStatus: GatewayCheckStatus;
  gatewayCheckMessage: string | null;
  errorMessage: string | null;
  isLoading: boolean;
  canSubmit: boolean;
  workspaceRootPlaceholder: string;
  cancelLabel: string;
  submitLabel: string;
  submitBusyLabel: string;
  // UiPath fields
  uipathOrgName: string;
  uipathTenantName: string;
  uipathClientId: string;
  uipathClientSecret: string;
  uipathFolderName: string;
  uipathProcessKey: string;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
  onCancel: () => void;
  onNameChange: (next: string) => void;
  onGatewayTypeChange: (next: string) => void;
  onGatewayUrlChange: (next: string) => void;
  onGatewayTokenChange: (next: string) => void;
  onDisableDevicePairingChange: (next: boolean) => void;
  onWorkspaceRootChange: (next: string) => void;
  onAllowInsecureTlsChange: (next: boolean) => void;
  onUipathOrgNameChange: (next: string) => void;
  onUipathTenantNameChange: (next: string) => void;
  onUipathClientIdChange: (next: string) => void;
  onUipathClientSecretChange: (next: string) => void;
  onUipathFolderNameChange: (next: string) => void;
  onUipathProcessKeyChange: (next: string) => void;
};

function ToggleSwitch({
  checked,
  label,
  disabled,
  onChange,
}: {
  checked: boolean;
  label: string;
  disabled: boolean;
  onChange: (next: boolean) => void;
}) {
  return (
    <button
      type="button"
      role="switch"
      aria-checked={checked}
      aria-label={label}
      onClick={() => onChange(!checked)}
      disabled={disabled}
      className={`inline-flex h-6 w-11 shrink-0 items-center rounded-full border transition ${
        checked ? "border-emerald-600 bg-emerald-600" : "border-slate-300 bg-slate-200"
      } ${disabled ? "cursor-not-allowed opacity-60" : "cursor-pointer"}`}
    >
      <span
        className={`inline-block h-5 w-5 rounded-full bg-white shadow-sm transition ${
          checked ? "translate-x-5" : "translate-x-0.5"
        }`}
      />
    </button>
  );
}

export function GatewayForm({
  name,
  gatewayType,
  gatewayUrl,
  gatewayToken,
  disableDevicePairing,
  workspaceRoot,
  allowInsecureTls,
  gatewayUrlError,
  gatewayCheckStatus,
  gatewayCheckMessage,
  errorMessage,
  isLoading,
  canSubmit,
  workspaceRootPlaceholder,
  cancelLabel,
  submitLabel,
  submitBusyLabel,
  uipathOrgName,
  uipathTenantName,
  uipathClientId,
  uipathClientSecret,
  uipathFolderName,
  uipathProcessKey,
  onSubmit,
  onCancel,
  onNameChange,
  onGatewayTypeChange,
  onGatewayUrlChange,
  onGatewayTokenChange,
  onDisableDevicePairingChange,
  onWorkspaceRootChange,
  onAllowInsecureTlsChange,
  onUipathOrgNameChange,
  onUipathTenantNameChange,
  onUipathClientIdChange,
  onUipathClientSecretChange,
  onUipathFolderNameChange,
  onUipathProcessKeyChange,
}: GatewayFormProps) {
  const isUiPath = gatewayType === GATEWAY_TYPE_UIPATH;

  return (
    <form
      onSubmit={onSubmit}
      className="space-y-6 rounded-xl border border-slate-200 bg-white p-6 shadow-sm"
    >
      <div className="space-y-2">
        <label className="text-sm font-medium text-slate-900">
          Gateway name <span className="text-red-500">*</span>
        </label>
        <Input
          value={name}
          onChange={(event) => onNameChange(event.target.value)}
          placeholder="Primary gateway"
          disabled={isLoading}
        />
      </div>

      <div className="space-y-2">
        <label className="text-sm font-medium text-slate-900">
          Gateway type <span className="text-red-500">*</span>
        </label>
        <div className="flex gap-3">
          {[
            { value: GATEWAY_TYPE_OPENCLAW, label: "OpenClaw" },
            { value: GATEWAY_TYPE_UIPATH, label: "UiPath Orchestrator" },
          ].map(({ value, label }) => (
            <button
              key={value}
              type="button"
              onClick={() => onGatewayTypeChange(value)}
              disabled={isLoading}
              className={`rounded-lg border px-4 py-2 text-sm font-medium transition ${
                gatewayType === value
                  ? "border-slate-900 bg-slate-900 text-white"
                  : "border-slate-200 bg-white text-slate-700 hover:border-slate-400"
              } ${isLoading ? "cursor-not-allowed opacity-60" : "cursor-pointer"}`}
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      {isUiPath ? (
        <>
          <div className="rounded-lg border border-blue-100 bg-blue-50 px-4 py-3 text-sm text-blue-700">
            Configure your UiPath Automation Cloud credentials below. After saving, use
            the{" "}
            <strong>Setup Webhook</strong> button on the gateway detail page to register
            the OpenClaw callback in UiPath Orchestrator.
          </div>
          <div className="grid gap-6 md:grid-cols-2">
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-900">
                Organization name <span className="text-red-500">*</span>
              </label>
              <Input
                value={uipathOrgName}
                onChange={(e) => onUipathOrgNameChange(e.target.value)}
                placeholder="my-org"
                disabled={isLoading}
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-900">
                Tenant name <span className="text-red-500">*</span>
              </label>
              <Input
                value={uipathTenantName}
                onChange={(e) => onUipathTenantNameChange(e.target.value)}
                placeholder="DefaultTenant"
                disabled={isLoading}
              />
            </div>
          </div>
          <div className="grid gap-6 md:grid-cols-2">
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-900">
                Client ID <span className="text-red-500">*</span>
              </label>
              <Input
                value={uipathClientId}
                onChange={(e) => onUipathClientIdChange(e.target.value)}
                placeholder="API app client ID"
                disabled={isLoading}
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-900">
                Client secret <span className="text-red-500">*</span>
              </label>
              <Input
                type="password"
                value={uipathClientSecret}
                onChange={(e) => onUipathClientSecretChange(e.target.value)}
                placeholder="API app client secret"
                disabled={isLoading}
              />
            </div>
          </div>
          <div className="grid gap-6 md:grid-cols-2">
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-900">
                Folder name <span className="text-red-500">*</span>
              </label>
              <Input
                value={uipathFolderName}
                onChange={(e) => onUipathFolderNameChange(e.target.value)}
                placeholder="Shared"
                disabled={isLoading}
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-900">
                Process key <span className="text-red-500">*</span>
              </label>
              <Input
                value={uipathProcessKey}
                onChange={(e) => onUipathProcessKeyChange(e.target.value)}
                placeholder="MyProcess"
                disabled={isLoading}
              />
            </div>
          </div>
        </>
      ) : (
        <>
          <div className="grid gap-6 md:grid-cols-2">
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-900">
                Gateway URL <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <Input
                  value={gatewayUrl}
                  onChange={(event) => onGatewayUrlChange(event.target.value)}
                  placeholder="ws://gateway:18789"
                  disabled={isLoading}
                  className={gatewayUrlError ? "border-red-500" : undefined}
                />
              </div>
              {gatewayUrlError ? (
                <p className="text-xs text-red-500">{gatewayUrlError}</p>
              ) : gatewayCheckStatus === "error" && gatewayCheckMessage ? (
                <p className="text-xs text-red-500">{gatewayCheckMessage}</p>
              ) : null}
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-900">
                Gateway token
              </label>
              <Input
                value={gatewayToken}
                onChange={(event) => onGatewayTokenChange(event.target.value)}
                placeholder="Bearer token"
                disabled={isLoading}
              />
            </div>
          </div>

          <div className="grid gap-6 md:grid-cols-2">
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-900">
                Workspace root <span className="text-red-500">*</span>
              </label>
              <Input
                value={workspaceRoot}
                onChange={(event) => onWorkspaceRootChange(event.target.value)}
                placeholder={workspaceRootPlaceholder}
                disabled={isLoading}
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-900">
                Disable device pairing
              </label>
              <label className="flex h-10 items-center gap-3 px-1 text-sm text-slate-900">
                <ToggleSwitch
                  checked={disableDevicePairing}
                  label="Disable device pairing"
                  disabled={isLoading}
                  onChange={onDisableDevicePairingChange}
                />
              </label>
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-900">
              Allow self-signed TLS certificates
            </label>
            <label className="flex h-10 items-center gap-3 px-1 text-sm text-slate-900">
              <ToggleSwitch
                checked={allowInsecureTls}
                label="Allow self-signed TLS certificates"
                disabled={isLoading}
                onChange={onAllowInsecureTlsChange}
              />
            </label>
          </div>
        </>
      )}

      {errorMessage ? (
        <p className="text-sm text-red-500">{errorMessage}</p>
      ) : null}

      <div className="flex justify-end gap-3">
        <Button
          type="button"
          variant="ghost"
          onClick={onCancel}
          disabled={isLoading}
        >
          {cancelLabel}
        </Button>
        <Button type="submit" disabled={isLoading || !canSubmit}>
          {isLoading ? submitBusyLabel : submitLabel}
        </Button>
      </div>
    </form>
  );
}
