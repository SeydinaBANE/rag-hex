import type { NextAuthOptions } from "next-auth";
import CredentialsProvider from "next-auth/providers/credentials";

export const authOptions: NextAuthOptions = {
  providers: [
    CredentialsProvider({
      name: "credentials",
      credentials: {
        username: { label: "Identifiant" },
        password: { label: "Mot de passe", type: "password" },
      },
      async authorize(credentials) {
        const username = process.env.AUTH_USERNAME;
        const password = process.env.AUTH_PASSWORD;

        if (
          credentials?.username === username &&
          credentials?.password === password
        ) {
          return { id: "1", name: username };
        }
        return null;
      },
    }),
  ],
  session: { strategy: "jwt" },
  pages: { signIn: "/login" },
};
