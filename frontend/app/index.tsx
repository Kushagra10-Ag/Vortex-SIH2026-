import { Redirect } from 'expo-router';

export default function Index() {
  // In production: check auth state and redirect accordingly
  // For demo: go straight to login
  return <Redirect href="/login" />;
}
