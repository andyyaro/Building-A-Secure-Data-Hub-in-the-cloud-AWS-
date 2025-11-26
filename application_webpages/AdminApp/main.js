// main.js

// Import UserManager directly from a CDN ESM build
import { UserManager } from "https://cdnjs.cloudflare.com/ajax/libs/oidc-client-ts/3.3.0/esm/oidc-client-ts.min.js";

// Hosted UI domain for your Cognito User Pool
const cognitoDomain = "https://<YOUR_COGNITO_HOSTED_UI_DOMAIN>";

// Core Cognito / OIDC config
const cognitoAuthConfig = {
  // Cognito User Pool issuer URL
  authority: "https://cognito-idp.<YOUR_AWS_REGION>.amazonaws.com/<YOUR_USER_POOL_ID>",

  // App client ID (no client secret for SPA)
  client_id: "<YOUR_APP_CLIENT_ID>",

  // IMPORTANT: must match callback URL configured in Cognito
  redirect_uri: "https://<YOUR_ADMIN_APP_DOMAIN>/callback.html",

  response_type: "code",
  scope: "email openid phone",

  // Where you want to land after logout
  post_logout_redirect_uri: "https://<YOUR_ADMIN_APP_DOMAIN>/",
};

// Create a UserManager instance that other scripts can import
export const userManager = new UserManager({
  ...cognitoAuthConfig,
});

// Sign-out redirect helper
export async function signOutRedirect() {
  try {
    // 1. Clear cached user from oidc-client-ts (localStorage / sessionStorage)
    await userManager.removeUser();
  } catch (e) {
    console.warn("Failed to remove local user from storage:", e);
    // not fatal – still continue to hit Cognito logout
  }

  // 2. Redirect to Cognito Hosted UI /logout endpoint
  const clientId = cognitoAuthConfig.client_id;
  const logoutUri = cognitoAuthConfig.post_logout_redirect_uri;

  window.location.href = `${cognitoDomain}/logout?client_id=${clientId}&logout_uri=${encodeURIComponent(
    logoutUri
  )}`;
}
