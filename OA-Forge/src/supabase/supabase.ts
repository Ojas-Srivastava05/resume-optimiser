import { createClient, type SupabaseClient } from "@supabase/supabase-js";

let client: SupabaseClient | null = null;

export function getSupabase(): SupabaseClient {
	if (!client) {
		const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || "https://placeholder-project.supabase.co";
		const supabaseKey =
			process.env.SUPABASE_SERVICE_ROLE_KEY ||
			process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ||
			"placeholder-key";
		client = createClient(supabaseUrl, supabaseKey);
	}
	return client;
}

/** Lazy singleton — avoids Supabase init during Next.js build import phase. */
export const supabase = new Proxy({} as SupabaseClient, {
	get(_target, prop, receiver) {
		return Reflect.get(getSupabase(), prop, receiver);
	},
});
