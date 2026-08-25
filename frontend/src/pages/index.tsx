import Head from "next/head";

import { ChatDashboard } from "@/components/ChatDashboard";

export default function Home() {
  return (
    <>
      <Head>
        <title>SmartWMS AI Operations Agent</title>
        <meta
          name="description"
          content="Demo WMS AI chat dashboard for inventory and operations questions"
        />
      </Head>
      <ChatDashboard />
    </>
  );
}
