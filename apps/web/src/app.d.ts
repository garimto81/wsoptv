/// <reference types="@sveltejs/kit" />

// App 네임스페이스 정의
declare global {
  namespace App {
    interface Locals {
      user?: import('$features/auth').User;
    }
    interface PageData {
      user?: import('$features/auth').User;
    }
    // interface Error {}
    // interface Platform {}
  }
}

export {};
