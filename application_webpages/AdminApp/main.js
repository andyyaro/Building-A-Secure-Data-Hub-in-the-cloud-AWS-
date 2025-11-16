// main.js

// Import UserManager directly from a CDN ESM build
import { UserManager } from "https://cdnjs.cloudflare.com/ajax/libs/oidc-client-ts/3.3.0/esm/oidc-client-ts.min.js";

const cognitoDomain =
  "https://us-east-1kbtkse7wb.auth.us-east-1.amazoncognito.com";

const cognitoAuthConfig = {
  authority: "https://cognito-idp.us-east-1.amazonaws.com/us-east-1_KbTkSe7WB",
  client_id: "oi3e134tcglfb3f90mkeqami1",
  // IMPORTANT: must match callback URL configured in Cognito
  redirect_uri: "https://admin.bytechisel.com/callback.html",
  response_type: "code",
  scope: "email openid phone",
  // Where you want to land after logout
  post_logout_redirect_uri: "https://admin.bytechisel.com/",
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
