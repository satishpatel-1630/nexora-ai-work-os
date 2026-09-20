import type {Metadata} from "next";import "./globals.css";import {Nav} from "../components/Nav";
export const metadata:Metadata={title:"NEXORA — Personal AI Work OS",description:"Research. Plan. Execute. Evaluate. Automate."};
export default function RootLayout({children}:Readonly<{children:React.ReactNode}>){return <html lang="en"><body><Nav/>{children}</body></html>}