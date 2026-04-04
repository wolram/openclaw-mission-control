"use client";

export const dynamic = "force-dynamic";

import { useState } from "react";
import { useRouter } from "next/navigation";

import { useAuth } from "@/auth/clerk";

import { ApiError } from "@/api/mutator";
import { useCreateGatewayApiV1GatewaysPost } from "@/api/generated/gateways/gateways";
import { useOrganizationMembership } from "@/lib/use-organization-membership";
import {
  GATEWAY_TYPE_OPENCLAW,
  GATEWAY_TYPE_UIPATH,
  GatewayForm,
} from "@/components/gateways/GatewayForm";
import { DashboardPageLayout } from "@/components/templates/DashboardPageLayout";
import {
  DEFAULT_WORKSPACE_ROOT,
  checkGatewayConnection,
  type GatewayCheckStatus,
  validateGatewayUrl,
} from "@/lib/gateway-form";

export default function NewGatewayPage() {
  const { isSignedIn } = useAuth();
  const router = useRouter();

  const { isAdmin } = useOrganizationMembership(isSignedIn);

  const [name, setName] = useState("");
  const [gatewayType, setGatewayType] = useState(GATEWAY_TYPE_OPENCLAW);
  const [gatewayUrl, setGatewayUrl] = useState("");
  const [gatewayToken, setGatewayToken] = useState("");
  const [disableDevicePairing, setDisableDevicePairing] = useState(false);
  const [workspaceRoot, setWorkspaceRoot] = useState(DEFAULT_WORKSPACE_ROOT);
  const [allowInsecureTls, setAllowInsecureTls] = useState(false);

  // UiPath fields
  const [uipathOrgName, setUipathOrgName] = useState("");
  const [uipathTenantName, setUipathTenantName] = useState("");
  const [uipathClientId, setUipathClientId] = useState("");
  const [uipathClientSecret, setUipathClientSecret] = useState("");
  const [uipathFolderName, setUipathFolderName] = useState("");
  const [uipathProcessKey, setUipathProcessKey] = useState("");

  const [gatewayUrlError, setGatewayUrlError] = useState<string | null>(null);
  const [gatewayCheckStatus, setGatewayCheckStatus] =
    useState<GatewayCheckStatus>("idle");
  const [gatewayCheckMessage, setGatewayCheckMessage] = useState<string | null>(
    null,
  );

  const [error, setError] = useState<string | null>(null);

  const createMutation = useCreateGatewayApiV1GatewaysPost<ApiError>({
    mutation: {
      onSuccess: (result) => {
        if (result.status === 200) {
          router.push(`/gateways/${result.data.id}`);
        }
      },
      onError: (err) => {
        setError(err.message || "Something went wrong.");
      },
    },
  });

  const isUiPath = gatewayType === GATEWAY_TYPE_UIPATH;
  const isLoading =
    createMutation.isPending || gatewayCheckStatus === "checking";

  const canSubmit = isUiPath
    ? Boolean(name.trim()) &&
      Boolean(uipathOrgName.trim()) &&
      Boolean(uipathTenantName.trim()) &&
      Boolean(uipathClientId.trim()) &&
      Boolean(uipathClientSecret.trim()) &&
      Boolean(uipathFolderName.trim()) &&
      Boolean(uipathProcessKey.trim())
    : Boolean(name.trim()) &&
      Boolean(gatewayUrl.trim()) &&
      Boolean(workspaceRoot.trim());

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!isSignedIn) return;

    if (!name.trim()) {
      setError("Gateway name is required.");
      return;
    }

    if (isUiPath) {
      setError(null);
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      createMutation.mutate({
        data: {
          name: name.trim(),
          url: "",
          workspace_root: "",
          gateway_type: GATEWAY_TYPE_UIPATH,
          uipath_org_name: uipathOrgName.trim(),
          uipath_tenant_name: uipathTenantName.trim(),
          uipath_client_id: uipathClientId.trim(),
          uipath_client_secret: uipathClientSecret.trim(),
          uipath_folder_name: uipathFolderName.trim(),
          uipath_process_key: uipathProcessKey.trim(),
        } as any, // eslint-disable-line @typescript-eslint/no-explicit-any
      });
      return;
    }

    const gatewayValidation = validateGatewayUrl(gatewayUrl);
    setGatewayUrlError(gatewayValidation);
    if (gatewayValidation) {
      setGatewayCheckStatus("error");
      setGatewayCheckMessage(gatewayValidation);
      return;
    }
    if (!workspaceRoot.trim()) {
      setError("Workspace root is required.");
      return;
    }

    setGatewayCheckStatus("checking");
    setGatewayCheckMessage(null);
    const { ok, message } = await checkGatewayConnection({
      gatewayUrl,
      gatewayToken,
      gatewayDisableDevicePairing: disableDevicePairing,
      gatewayAllowInsecureTls: allowInsecureTls,
    });
    setGatewayCheckStatus(ok ? "success" : "error");
    setGatewayCheckMessage(message);
    if (!ok) {
      return;
    }

    setError(null);
    createMutation.mutate({
      data: {
        name: name.trim(),
        url: gatewayUrl.trim(),
        token: gatewayToken.trim() || null,
        disable_device_pairing: disableDevicePairing,
        workspace_root: workspaceRoot.trim(),
        allow_insecure_tls: allowInsecureTls,
      },
    });
  };

  return (
    <DashboardPageLayout
      signedOut={{
        message: "Sign in to create a gateway.",
        forceRedirectUrl: "/gateways/new",
      }}
      title="Create gateway"
      description="Configure an OpenClaw or UiPath Orchestrator gateway."
      isAdmin={isAdmin}
      adminOnlyMessage="Only organization owners and admins can create gateways."
    >
      <GatewayForm
        name={name}
        gatewayType={gatewayType}
        gatewayUrl={gatewayUrl}
        gatewayToken={gatewayToken}
        disableDevicePairing={disableDevicePairing}
        workspaceRoot={workspaceRoot}
        allowInsecureTls={allowInsecureTls}
        gatewayUrlError={gatewayUrlError}
        gatewayCheckStatus={gatewayCheckStatus}
        gatewayCheckMessage={gatewayCheckMessage}
        errorMessage={error}
        isLoading={isLoading}
        canSubmit={canSubmit}
        workspaceRootPlaceholder={DEFAULT_WORKSPACE_ROOT}
        cancelLabel="Cancel"
        submitLabel="Create gateway"
        submitBusyLabel="Creating…"
        uipathOrgName={uipathOrgName}
        uipathTenantName={uipathTenantName}
        uipathClientId={uipathClientId}
        uipathClientSecret={uipathClientSecret}
        uipathFolderName={uipathFolderName}
        uipathProcessKey={uipathProcessKey}
        onSubmit={handleSubmit}
        onCancel={() => router.push("/gateways")}
        onNameChange={setName}
        onGatewayTypeChange={(next) => {
          setGatewayType(next);
          setGatewayUrlError(null);
          setGatewayCheckStatus("idle");
          setGatewayCheckMessage(null);
          setError(null);
        }}
        onGatewayUrlChange={(next) => {
          setGatewayUrl(next);
          setGatewayUrlError(null);
          setGatewayCheckStatus("idle");
          setGatewayCheckMessage(null);
        }}
        onGatewayTokenChange={(next) => {
          setGatewayToken(next);
          setGatewayCheckStatus("idle");
          setGatewayCheckMessage(null);
        }}
        onDisableDevicePairingChange={(next) => {
          setDisableDevicePairing(next);
          setGatewayCheckStatus("idle");
          setGatewayCheckMessage(null);
        }}
        onWorkspaceRootChange={setWorkspaceRoot}
        onAllowInsecureTlsChange={(next) => {
          setAllowInsecureTls(next);
          setGatewayCheckStatus("idle");
          setGatewayCheckMessage(null);
        }}
        onUipathOrgNameChange={setUipathOrgName}
        onUipathTenantNameChange={setUipathTenantName}
        onUipathClientIdChange={setUipathClientId}
        onUipathClientSecretChange={setUipathClientSecret}
        onUipathFolderNameChange={setUipathFolderName}
        onUipathProcessKeyChange={setUipathProcessKey}
      />
    </DashboardPageLayout>
  );
}
