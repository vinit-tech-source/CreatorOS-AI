import { PageHeader } from '../../components/layout/PageHeader';
import { Card, CardContent, CardHeader } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';
import { useAuthStore } from '../../stores/authStore';

export function Settings() {
  const { user } = useAuthStore();

  return (
    <div className="flex-col gap-6">
      <PageHeader title="Settings" subtitle="Manage your account preferences" />

      <div className="max-w-2xl">
        <Card glass className="mb-6">
          <CardHeader title="Profile Information" />
          <CardContent>
            <form className="flex flex-col gap-4">
              <div className="flex gap-4">
                <Input label="First Name" defaultValue={user?.first_name || ''} />
                <Input label="Last Name" defaultValue={user?.last_name || ''} />
              </div>
              <Input label="Email Address" type="email" defaultValue={user?.email || ''} disabled />
              
              <div className="mt-4">
                <Button>Save Changes</Button>
              </div>
            </form>
          </CardContent>
        </Card>

        <Card glass>
          <CardHeader title="Danger Zone" className="text-red-500" />
          <CardContent>
            <p className="text-sm text-secondary mb-4">
              Once you delete your account, there is no going back. Please be certain.
            </p>
            <Button variant="danger">Delete Account</Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
